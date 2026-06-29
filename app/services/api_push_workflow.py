from pathlib import Path
import json
import re
from typing import Any

import pandas as pd
from docx import Document
from pypdf import PdfReader

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, GENERATED_DIR, REPORT_DIR, ensure_workspace
from app.models.schema import ApiPushResult, FieldMapping, FieldSchema, MappingStatus
from app.services.document_parser import _read_table, _to_bool
from app.services.field_matcher import generate_mapping_table
from app.services.llm_mapping_enhancer import apply_knowledge_hints, enhance_mappings_with_deepseek
from app.services.mapping_review import export_mapping_review_excel
from app.services.mapping_validator import validate_mappings_against_source_schema
from app.services.knowledge_base import extract_file_text
from app.utils.json_utils import dump_json


DB_REQUIRED_COLUMNS = {"table_name", "column_name", "description", "type", "required", "example"}
API_REQUIRED_COLUMNS = {"endpoint", "method", "param_path", "param_name", "description", "type", "required", "example"}

DB_COLUMN_ALIASES = {
    "table_name": {"table_name", "table", "表名", "数据表", "資料表", "table name"},
    "column_name": {"column_name", "column", "field_name", "字段名", "欄位名", "字段", "栏位", "field", "name"},
    "description": {"description", "field_description", "字段说明", "字段說明", "说明", "說明", "备注", "remark", "comment"},
    "type": {"type", "data_type", "字段类型", "字段類型", "类型", "類型", "数据类型", "資料型態"},
    "required": {"required", "mandatory", "必填", "是否必填", "允许空", "允許空", "nullable", "null"},
    "example": {"example", "sample", "示例", "范例", "範例", "默认值", "默認值", "default", "default_value"},
}

API_COLUMN_ALIASES = {
    "endpoint": {"endpoint", "url", "api", "api_url", "接口地址", "请求地址", "請求地址", "接口url", "path"},
    "method": {"method", "http_method", "请求方式", "請求方式", "方法"},
    "param_path": {
        "param_path",
        "node",
        "json_path",
        "field_path",
        "字段路径",
        "字段路徑",
        "参数路径",
        "參數路徑",
        "节点路径",
        "節點路徑",
    },
    "param_name": {"param_name", "field_name", "parameter", "param", "node", "字段名", "参数名", "參數名", "name"},
    "description": {"description", "字段说明", "字段說明", "说明", "說明", "备注", "remark", "comment"},
    "type": {"type", "data_type", "format", "字段类型", "字段類型", "类型", "類型", "数据类型", "資料型態"},
    "required": {"required", "mandatory", "必填", "是否必填", "是否必须", "是否必須", "required?", "是否为空"},
    "example": {"example", "sample", "示例", "范例", "範例", "样例", "樣例"},
}

CANONICAL_COLUMN_PRIORITY = {
    "table_name": ["table_name", "表名", "数据表", "資料表", "table"],
    "column_name": ["column_name", "字段名", "欄位名", "field_name", "column", "field"],
    "description": ["字段说明", "字段說明", "field_description", "description", "comment", "remark", "说明", "說明"],
    "type": ["data_type", "字段类型", "字段類型", "数据类型", "資料型態", "format", "type", "类型", "類型"],
    "required": ["required", "mandatory", "必填", "是否必填", "允许空", "允許空", "nullable", "null"],
    "example": ["example", "sample", "示例", "样例", "樣例", "范例", "範例", "默认值", "默認值", "default"],
    "endpoint": ["endpoint", "api_url", "接口地址", "请求地址", "請求地址", "url", "api"],
    "method": ["method", "http_method", "请求方式", "請求方式", "方法"],
    "param_path": ["param_path", "json_path", "field_path", "字段路径", "字段路徑", "参数路径", "參數路徑", "node"],
    "param_name": ["param_name", "参数名", "參數名", "field_name", "字段名", "parameter", "param", "node", "name"],
}


def _clean(value: Any, default: str = "") -> str:
    if pd.isna(value):
        return default
    return str(value).strip()


def _norm_header(value: Any) -> str:
    return re.sub(r"[\s_\-/()（）]+", "", _clean(value).lower())


def _alias_lookup(aliases: dict[str, set[str]]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for canonical, names in aliases.items():
        for name in names:
            lookup[_norm_header(name)] = canonical
    return lookup


def _normalize_columns(df: pd.DataFrame, aliases: dict[str, set[str]]) -> pd.DataFrame:
    lookup = _alias_lookup(aliases)
    rename: dict[Any, str] = {}
    source_names: dict[str, str] = {}
    candidates: dict[str, list[Any]] = {}
    for column in df.columns:
        canonical = lookup.get(_norm_header(column))
        if canonical:
            candidates.setdefault(canonical, []).append(column)
    for canonical, columns in candidates.items():
        priorities = [_norm_header(item) for item in CANONICAL_COLUMN_PRIORITY.get(canonical, [])]
        chosen = sorted(
            columns,
            key=lambda column: priorities.index(_norm_header(column)) if _norm_header(column) in priorities else len(priorities),
        )[0]
        rename[chosen] = canonical
        source_names[canonical] = str(chosen)
    normalized = df.rename(columns=rename)
    for canonical, source_name in source_names.items():
        normalized[f"__source_column_{canonical}"] = source_name
    return normalized.loc[:, ~normalized.columns.duplicated()]


def _detect_header_row(raw: pd.DataFrame, aliases: dict[str, set[str]], min_hits: int) -> int | None:
    lookup = _alias_lookup(aliases)
    for index, row in raw.iterrows():
        hits = sum(1 for value in row.tolist() if lookup.get(_norm_header(value)))
        if hits >= min_hits:
            return int(index)
    return None


def _read_excel_tables(path: str | Path, aliases: dict[str, set[str]], min_hits: int) -> list[pd.DataFrame]:
    tables: list[pd.DataFrame] = []
    excel = pd.ExcelFile(path)
    for sheet in excel.sheet_names:
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
        header_row = _detect_header_row(raw, aliases, min_hits)
        if header_row is None:
            continue
        headers = raw.iloc[header_row].tolist()
        table = raw.iloc[header_row + 1 :].copy()
        table.columns = headers
        table = table.dropna(how="all")
        if not table.empty:
            tables.append(_normalize_columns(table, aliases))
    return tables


def _read_docx_tables(path: str | Path) -> list[pd.DataFrame]:
    document = Document(str(path))
    tables: list[pd.DataFrame] = []
    for table in document.tables:
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        if len(rows) < 2:
            continue
        headers = [header.strip() for header in rows[0]]
        records = [row[: len(headers)] for row in rows[1:] if any(cell.strip() for cell in row)]
        if headers and records:
            tables.append(pd.DataFrame(records, columns=headers))
    return tables


def _extract_pdf_text(path: str | Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_pipe_table_from_text(text: str) -> pd.DataFrame | None:
    text = text.replace("example/", "example|/")
    text = re.sub(r"([A-Za-z0-9_.-])(/api)", r"\1|\2", text)
    lines = [line.strip() for line in text.splitlines() if "|" in line]
    rows: list[list[str]] = []
    for line in lines:
        if set(line.replace("|", "").strip()) <= {"-", ":"}:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 3:
            rows.append(cells)
    if len(rows) < 2:
        cells = [cell.strip() for cell in text.replace("\n", "|").strip("|").split("|") if cell.strip()]
        if len(cells) < 16:
            return None
        header_size = 8
        headers = cells[:header_size]
        records = [cells[index : index + header_size] for index in range(header_size, len(cells), header_size)]
        records = [record for record in records if len(record) == header_size]
        return pd.DataFrame(records, columns=headers) if records else None

    headers = rows[0]
    records = [row[: len(headers)] for row in rows[1:] if len(row) >= len(headers)]
    return pd.DataFrame(records, columns=headers) if records else None


def _read_document_table(
    path: str | Path,
    required_columns: set[str],
    label: str,
    aliases: dict[str, set[str]],
    min_hits: int = 3,
) -> pd.DataFrame:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".csv":
        return _normalize_columns(_read_table(source), aliases)
    if suffix in {".xlsx", ".xls"}:
        tables = _read_excel_tables(source, aliases, min_hits)
        if tables:
            return pd.concat(tables, ignore_index=True)
        return _normalize_columns(_read_table(source), aliases)

    if suffix == ".docx":
        tables: list[pd.DataFrame] = []
        for table in _read_docx_tables(source):
            table = _normalize_columns(table, aliases)
            if len(required_columns & set(table.columns)) >= min_hits:
                tables.append(table)
        if tables:
            return pd.concat(tables, ignore_index=True)
        raise ValueError(f"No Word table contains required {label} columns: {', '.join(sorted(required_columns))}")

    if suffix == ".pdf":
        table = _read_pipe_table_from_text(_extract_pdf_text(source))
        if table is None:
            raise ValueError(
                "Could not extract a structured table from PDF. "
                "Use a text PDF with a pipe-delimited field table, Word table, CSV, or Excel. "
                "Scanned PDF OCR is not supported in this MVP."
            )
        return _normalize_columns(table, aliases)

    raise ValueError(f"Unsupported {label} document format: {source.suffix}")


def parse_database_document(path: str | Path) -> list[FieldSchema]:
    """Parse a database data dictionary into FieldSchema objects."""
    df = _read_document_table(path, DB_REQUIRED_COLUMNS, "database", DB_COLUMN_ALIASES, min_hits=4)
    df.columns = [str(column).strip() for column in df.columns]
    if "required" not in df.columns and "nullable" in df.columns:
        df["required"] = df["nullable"]
    if "required" not in df.columns:
        df["required"] = True
    if "example" not in df.columns:
        df["example"] = None
    missing = {"table_name", "column_name", "description", "type"} - set(df.columns)
    if missing:
        raise ValueError(f"Database document is missing columns: {', '.join(sorted(missing))}")

    df["table_name"] = df["table_name"].ffill()

    fields: list[FieldSchema] = []
    for _, row in df.iterrows():
        table_name = _clean(row["table_name"])
        column_name = _clean(row["column_name"])
        if not column_name:
            continue
        required_value = row["required"]
        required_source = _clean(row.get("__source_column_required", "required"))
        required = _to_bool(required_value)
        if _norm_header(required_source) in {_norm_header("允许空"), _norm_header("允許空"), _norm_header("nullable"), _norm_header("null")}:
            required = not _to_bool(required_value)
        fields.append(
            FieldSchema(
                field_name=f"{table_name}.{column_name}" if table_name else column_name,
                description=_clean(row["description"]),
                type=_clean(row["type"], "string").lower(),
                required=required,
                example=None if pd.isna(row["example"]) else row["example"],
            )
        )
    return fields


def _infer_type_from_example(value: str) -> str:
    text = value.strip().strip(",").strip('"')
    if text in {"{", "["}:
        return "object"
    if text in {"", "null"}:
        return "string"
    if text.lower() in {"true", "false"}:
        return "boolean"
    if re.fullmatch(r"-?\d+(\.\d+)?", text):
        return "number"
    return "string"


def _parse_api_document_from_json_template(path: str | Path) -> tuple[str, str, list[FieldSchema]]:
    text = extract_file_text(path).replace('""', '"')
    fields: list[FieldSchema] = []
    seen: set[str] = set()
    for line in text.splitlines():
        match = re.search(r'"([^"]+)"\s*:\s*([^,\n\r]*)', line)
        if not match:
            continue
        field_name = match.group(1).strip()
        if field_name in {"root"} or field_name in seen:
            continue
        raw_value = match.group(2).strip()
        clean_value = raw_value.strip().strip(",").strip('"').strip()
        if clean_value in {"{", "["}:
            continue
        seen.add(field_name)
        fields.append(
            FieldSchema(
                field_name=field_name,
                description=line.strip(),
                type=_infer_type_from_example(raw_value),
                required=False,
                example=raw_value.strip().strip(",").strip('"') or None,
            )
        )
    if not fields:
        raise ValueError(
            "API document is missing columns: description, param_path, type. "
            "It also could not be parsed as a JSON template document."
        )
    return "/", "POST", fields


def _parse_bool(value: Any) -> bool:
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "required", "mandatory", "m", "是", "必填", "√"}


def _parse_api_document_with_deepseek(path: str | Path) -> tuple[str, str, list[FieldSchema]]:
    if not DEEPSEEK_API_KEY:
        raise ValueError(
            "API document is missing columns: description, param_path, type. "
            "It also could not be parsed as a JSON template document. "
            "For free-form PDF/Word interface documents, configure DEEPSEEK_API_KEY and retry."
        )

    text = extract_file_text(path).strip()
    if len(text) < 80:
        raise ValueError(
            "Could not extract enough text from the API document. "
            "If this is a scanned PDF, OCR is required before parsing."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package is not installed. Run `pip install -r requirements.txt`.") from exc

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    prompt = {
        "task": "Extract target API/interface fields from this document.",
        "instructions": [
            "Return strict JSON only.",
            "Extract leaf fields, request/body fields, file columns, or manifest columns.",
            "Do not include section titles as fields.",
            "If the document describes a flat file, use the field/column name as param_path.",
            "If it describes JSON/XML, use node path or node name as param_path.",
        ],
        "response_schema": {
            "endpoint": "string, optional",
            "method": "string, optional",
            "fields": [
                {
                    "param_path": "target field path or column name",
                    "param_name": "short field name",
                    "description": "field meaning",
                    "type": "string/number/date/boolean/object or original format",
                    "required": "boolean",
                    "example": "optional sample value",
                }
            ],
        },
        "document_text": text[:50000],
    }
    completion = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an enterprise EDI/API specification parser. Return JSON only.",
            },
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    payload = json.loads(completion.choices[0].message.content or "{}")
    fields_payload = payload.get("fields") or []
    fields: list[FieldSchema] = []
    seen: set[str] = set()
    for item in fields_payload:
        if not isinstance(item, dict):
            continue
        field_name = str(item.get("param_path") or item.get("param_name") or "").strip()
        if not field_name or field_name in seen:
            continue
        seen.add(field_name)
        fields.append(
            FieldSchema(
                field_name=field_name,
                description=str(item.get("description") or "").strip(),
                type=str(item.get("type") or "string").strip().lower(),
                required=_parse_bool(item.get("required", False)),
                example=item.get("example"),
            )
        )
    if not fields:
        raise ValueError("DeepSeek could not extract API fields from this document.")
    return str(payload.get("endpoint") or "/"), str(payload.get("method") or "POST").upper(), fields


def parse_api_document(path: str | Path) -> tuple[str, str, list[FieldSchema]]:
    """Parse target API request documentation into endpoint metadata and fields."""
    try:
        df = _read_document_table(path, API_REQUIRED_COLUMNS, "API", API_COLUMN_ALIASES, min_hits=3)
    except ValueError:
        try:
            return _parse_api_document_from_json_template(path)
        except ValueError:
            return _parse_api_document_with_deepseek(path)
    df.columns = [str(column).strip() for column in df.columns]
    if "endpoint" not in df.columns:
        df["endpoint"] = "/"
    if "method" not in df.columns:
        df["method"] = "POST"
    if "param_path" not in df.columns and "param_name" in df.columns:
        df["param_path"] = df["param_name"]
    if "param_name" not in df.columns and "param_path" in df.columns:
        df["param_name"] = df["param_path"]
    if "example" not in df.columns:
        df["example"] = None
    if "required" not in df.columns:
        df["required"] = False
    missing = {"param_path", "description", "type"} - set(df.columns)
    if missing:
        try:
            return _parse_api_document_from_json_template(path)
        except ValueError:
            return _parse_api_document_with_deepseek(path)

    endpoint = _clean(df.iloc[0]["endpoint"], "/")
    method = _clean(df.iloc[0]["method"], "POST").upper()
    fields: list[FieldSchema] = []
    for _, row in df.iterrows():
        param_path = _clean(row["param_path"]) or _clean(row["param_name"])
        if not param_path:
            continue
        raw_type = row["type"]
        field_type = _clean(raw_type).lower()
        type_source = _clean(row.get("__source_column_type", "type"))
        if not field_type and _norm_header(type_source) == _norm_header("format"):
            continue
        if not field_type and param_path.lower().startswith("subnode"):
            continue
        fields.append(
            FieldSchema(
                field_name=param_path,
                description=_clean(row["description"]),
                type=field_type or "string",
                required=_to_bool(row["required"]),
                example=None if pd.isna(row["example"]) else row["example"],
            )
        )
    return endpoint, method, fields


def _default_value(field: FieldSchema) -> Any:
    if field.example not in (None, ""):
        return field.example
    if field.type in {"number", "int", "integer", "float", "decimal"}:
        return 0
    if field.type in {"bool", "boolean"}:
        return False
    if field.type in {"array", "list"}:
        return []
    if field.type in {"object", "dict"}:
        return {}
    return ""


def _set_nested(payload: dict[str, Any], dotted_path: str, value: Any) -> None:
    parts = [part for part in dotted_path.split(".") if part]
    cursor = payload
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})
    if parts:
        cursor[parts[-1]] = value


def build_payload_template(api_fields: list[FieldSchema]) -> dict[str, Any]:
    """Build target API JSON shape from dotted parameter paths."""
    payload: dict[str, Any] = {}
    for field in api_fields:
        _set_nested(payload, field.field_name, _default_value(field))
    return payload


def _mapping_table(mappings: list[FieldMapping]) -> str:
    lines = [
        "| db_column | api_param_path | confidence | status | reason |",
        "|---|---|---:|---|---|",
    ]
    for item in mappings:
        lines.append(
            f"| {item.source_field or ''} | {item.target_field} | "
            f"{item.confidence:.2f} | {item.status.value} | {item.reason} |"
        )
    return "\n".join(lines)


def generate_api_mapping_report(
    endpoint: str,
    method: str,
    mappings: list[FieldMapping],
    payload_template_path: str | Path,
    mapping_review_path: str | Path,
    report_dir: str | Path,
    llm_message: str = "",
) -> Path:
    target = Path(report_dir)
    target.mkdir(parents=True, exist_ok=True)
    report_path = target / "api_push_mapping_report.md"
    review = [item for item in mappings if item.status == MappingStatus.NEED_REVIEW]
    unmatched = [item for item in mappings if item.status == MappingStatus.UNMATCHED]
    content = f"""# API Push Mapping Report

## Target API

- Method: `{method}`
- Endpoint: `{endpoint}`
- Payload template: `{Path(payload_template_path).as_posix()}`
- Mapping review workbook: `{Path(mapping_review_path).as_posix()}`
- LLM: `{llm_message or "Not used."}`

## Database To API Mapping

{_mapping_table(mappings)}

## Need Human Review

{_mapping_table(review) if review else "No fields need review."}

## Unmatched API Fields

{_mapping_table(unmatched) if unmatched else "No unmatched API fields."}
"""
    report_path.write_text(content, encoding="utf-8")
    return report_path


def run_api_push_mapping_workflow(
    database_doc_path: str | Path,
    api_doc_path: str | Path,
    use_llm: bool = False,
    llm_max_targets: int | None = None,
) -> ApiPushResult:
    """Map database columns to target API request fields and emit reviewable artifacts."""
    ensure_workspace()
    db_fields = parse_database_document(database_doc_path)
    endpoint, method, api_fields = parse_api_document(api_doc_path)
    mappings = generate_mapping_table(db_fields, api_fields)
    mappings, rag_message = apply_knowledge_hints(mappings, db_fields, api_fields)
    llm_used = False
    llm_message = rag_message
    if use_llm:
        try:
            mappings, deepseek_message = enhance_mappings_with_deepseek(mappings, db_fields, api_fields, llm_max_targets)
            llm_message = f"{rag_message} {deepseek_message}"
            llm_used = True
        except Exception as exc:
            llm_message = f"{rag_message} DeepSeek skipped: {exc}"
    mappings, invalid_count = validate_mappings_against_source_schema(
        mappings,
        {field.field_name for field in db_fields},
    )
    if invalid_count:
        llm_message = f"{llm_message} Rejected {invalid_count} invalid source-field references."
    payload_template = build_payload_template(api_fields)
    payload_template_path = dump_json(payload_template, GENERATED_DIR / "target_api_payload_template.json")
    mapping_review_path = export_mapping_review_excel(mappings)
    report_path = generate_api_mapping_report(endpoint, method, mappings, payload_template_path, mapping_review_path, REPORT_DIR, llm_message)
    return ApiPushResult(
        endpoint=endpoint,
        method=method,
        mappings=mappings,
        payload_template_path=str(payload_template_path),
        mapping_report_path=str(report_path),
        mapping_review_path=str(mapping_review_path),
        llm_used=llm_used,
        llm_message=llm_message,
    )
