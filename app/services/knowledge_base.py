from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any
from uuid import uuid4

import pandas as pd
from docx import Document
from pypdf import PdfReader

from app.config import KNOWLEDGE_DIR, ensure_workspace
from app.models.schema import KnowledgeItem


KNOWLEDGE_STORE = KNOWLEDGE_DIR / "knowledge_items.json"


def _load_items() -> list[KnowledgeItem]:
    ensure_workspace()
    if not KNOWLEDGE_STORE.exists():
        return []
    data = json.loads(KNOWLEDGE_STORE.read_text(encoding="utf-8"))
    return [KnowledgeItem.model_validate(item) for item in data]


def _save_items(items: list[KnowledgeItem]) -> None:
    ensure_workspace()
    KNOWLEDGE_STORE.write_text(
        json.dumps([item.model_dump(mode="json") for item in items], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tags_match(existing_tags: list[str], requested_tags: list[str]) -> bool:
    return set(requested_tags).issubset(set(existing_tags))


def _existing_llm_items(source: Path, tags: list[str]) -> list[KnowledgeItem]:
    fingerprint = _file_fingerprint(source)
    matches: list[KnowledgeItem] = []
    fallback_matches: list[KnowledgeItem] = []
    for item in _load_items():
        metadata = item.metadata or {}
        if metadata.get("source_file") != source.name or not metadata.get("llm_extracted"):
            continue
        if not _tags_match(item.tags, tags):
            continue
        if metadata.get("source_fingerprint") == fingerprint:
            matches.append(item)
        elif "source_fingerprint" not in metadata:
            fallback_matches.append(item)
    return matches or fallback_matches


def list_knowledge_items() -> list[KnowledgeItem]:
    return sorted(_load_items(), key=lambda item: item.created_at, reverse=True)


def add_knowledge_item(
    title: str,
    content: str,
    category: str = "business_context",
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> KnowledgeItem:
    item = KnowledgeItem(
        id=str(uuid4()),
        title=title.strip() or "Untitled knowledge",
        category=category,
        content=content.strip(),
        tags=tags or [],
        metadata=metadata or {},
        created_at=datetime.now(UTC),
    )
    items = _load_items()
    items.append(item)
    _save_items(items)
    return item


def clear_knowledge_items() -> None:
    _save_items([])


def _tokens(text: str) -> set[str]:
    normalized = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text.lower())
    return {token for token in normalized.split() if len(token) > 1}


def search_knowledge(query: str, limit: int = 5) -> list[KnowledgeItem]:
    query_tokens = _tokens(query)
    if not query_tokens:
        return []
    scored: list[tuple[float, KnowledgeItem]] = []
    for item in _load_items():
        text = " ".join([item.title, item.category, item.content, " ".join(item.tags)])
        item_tokens = _tokens(text)
        if not item_tokens:
            continue
        overlap = len(query_tokens & item_tokens)
        if overlap == 0:
            continue
        category_boost = 1.25 if item.category in {"historical_mapping", "field_alias", "glossary"} else 1.0
        score = category_boost * overlap / max(len(query_tokens), 1)
        scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:limit]]


def _read_docx_text(path: Path) -> str:
    document = Document(str(path))
    chunks: list[str] = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                chunks.append(" | ".join(cells))
    return "\n".join(chunks)


def _read_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_file_text(path: str | Path) -> str:
    """Convert supported knowledge files into text for LLM extraction."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix in {".txt", ".md", ".json"}:
        return source.read_text(encoding="utf-8")
    if suffix == ".docx":
        return _read_docx_text(source)
    if suffix == ".pdf":
        return _read_pdf_text(source)
    if suffix in {".csv", ".xlsx", ".xls"}:
        chunks: list[str] = []
        if suffix == ".csv":
            chunks.append(pd.read_csv(source).fillna("").astype(str).to_csv(index=False))
        else:
            excel = pd.ExcelFile(source)
            for sheet in excel.sheet_names:
                df = pd.read_excel(source, sheet_name=sheet, header=None)
                chunks.append(f"# Sheet: {sheet}\n{df.fillna('').astype(str).to_csv(index=False, header=False)}")
        return "\n\n".join(chunks)
    raise ValueError(f"Unsupported knowledge file format: {source.suffix}")


def _ingest_tabular(path: Path, category: str, tags: list[str]) -> list[KnowledgeItem]:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    df.columns = [str(column).strip() for column in df.columns]
    created: list[KnowledgeItem] = []
    for index, row in df.iterrows():
        values = {column: "" if pd.isna(row[column]) else str(row[column]).strip() for column in df.columns}
        if not any(values.values()):
            continue
        title = values.get("title") or values.get("target_field") or values.get("api_field") or f"{path.stem} row {index + 1}"
        content = "\n".join(f"{key}: {value}" for key, value in values.items() if value)
        created.append(
            add_knowledge_item(
                title=title,
                content=content,
                category=values.get("category") or category,
                tags=tags,
                metadata={"source_file": path.name, "row": int(index) + 1},
            )
        )
    return created


def _extract_json_node(value: Any) -> str | None:
    text = "" if pd.isna(value) else str(value).strip()
    match = re.match(r'^"([^"]+)"\s*:', text)
    if not match:
        return None
    node = match.group(1).strip()
    if node in {"root"}:
        return None
    return node


def _extract_source_fields(text: str) -> list[str]:
    fields: list[str] = []
    for table, column in re.findall(r"\b([A-Z][A-Z0-9_]+)\.([A-Z0-9_ ]+)", text):
        clean_column = re.sub(r"\s+", "", column).strip("_")
        field_name = f"{table}.{clean_column}" if clean_column else ""
        if field_name and field_name not in fields:
            fields.append(field_name)
    return fields


def _extract_fixed_value(value: Any) -> str | None:
    text = "" if pd.isna(value) else str(value).strip().rstrip(",")
    match = re.match(r'^"[^"]+"\s*:\s*(.+)$', text)
    if not match:
        return None
    raw_value = match.group(1).strip()
    if raw_value in {"{", "[", "", "null"}:
        return None
    return raw_value.strip('"')


def _looks_like_integration_spec(df: pd.DataFrame) -> bool:
    node_count = 0
    for _, row in df.head(120).iterrows():
        if any(_extract_json_node(value) for value in row.tolist()):
            node_count += 1
    text = "\n".join(df.fillna("").astype(str).head(120).agg(" ".join, axis=1).tolist())
    return node_count >= 5 and ("IF 对应栏位" in text or "GFBL." in text or "GFBLCNT." in text)


def _ingest_integration_spec(path: Path, tags: list[str]) -> list[KnowledgeItem]:
    created: list[KnowledgeItem] = []
    excel = pd.ExcelFile(path)
    for sheet in excel.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, header=None)
        if not _looks_like_integration_spec(df):
            if sheet.lower() in {"containertype", "container_type"}:
                content = df.dropna(how="all").fillna("").astype(str).head(300).to_csv(index=False, header=False)
                created.append(
                    add_knowledge_item(
                        title=f"{path.stem} {sheet}",
                        content=f"Container ISO code reference table:\n{content}",
                        category="enum_mapping",
                        tags=[*tags, "container_type"],
                        metadata={"source_file": path.name, "sheet": sheet},
                    )
                )
            continue

        for index, row in df.iterrows():
            node_cell = next((value for value in row.tolist() if _extract_json_node(value)), None)
            target = _extract_json_node(node_cell)
            if not target:
                continue
            row_text = " | ".join("" if pd.isna(value) else str(value).strip() for value in row.tolist())
            source_fields = _extract_source_fields(row_text)
            fixed_value = _extract_fixed_value(node_cell)
            is_fixed = "固定" in row_text and not source_fields
            if not source_fields and not is_fixed and not row_text.strip():
                continue
            item_category = "historical_mapping" if source_fields else "fixed_value_rule" if is_fixed else "business_context"
            content_lines = [
                f"target_field: {target}",
                f"source_fields: {', '.join(source_fields) if source_fields else ''}",
                f"fixed_value: {fixed_value or ''}",
                f"notes: {row_text}",
            ]
            created.append(
                add_knowledge_item(
                    title=target,
                    content="\n".join(content_lines),
                    category=item_category,
                    tags=[*tags, "integration_spec"],
                    metadata={
                        "source_file": path.name,
                        "sheet": sheet,
                        "row": int(index) + 1,
                        "target_field": target,
                        "source_fields": source_fields,
                        "fixed_value": fixed_value,
                    },
                )
            )
    return created


def _add_llm_items(items: list[dict[str, Any]], fallback_category: str, tags: list[str]) -> list[KnowledgeItem]:
    created: list[KnowledgeItem] = []
    for item in items:
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        item_tags = [*tags, *[str(tag) for tag in item.get("tags", []) if str(tag).strip()]]
        created.append(
            add_knowledge_item(
                title=str(item.get("title") or content[:40]),
                content=content,
                category=str(item.get("category") or fallback_category),
                tags=list(dict.fromkeys(item_tags)),
                metadata=item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
            )
        )
    return created


def ingest_knowledge_file(
    path: str | Path,
    category: str = "business_context",
    tags: list[str] | None = None,
    use_llm: bool = False,
) -> list[KnowledgeItem]:
    source = Path(path)
    item_tags = tags or []
    if use_llm:
        existing = _existing_llm_items(source, item_tags)
        if existing:
            return existing

        from app.services.llm_knowledge_extractor import extract_knowledge_with_deepseek

        try:
            llm_items = extract_knowledge_with_deepseek(source.name, extract_file_text(source), item_tags)
            fingerprint = _file_fingerprint(source)
            for item in llm_items:
                metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
                metadata["source_fingerprint"] = fingerprint
                item["metadata"] = metadata
            created = _add_llm_items(llm_items, category, item_tags)
            if created:
                return created
        except Exception as exc:
            add_knowledge_item(
                title=f"{source.name} LLM extraction failed",
                content=f"DeepSeek knowledge extraction failed and rule fallback was used. Error: {exc}",
                category="business_context",
                tags=[*item_tags, "llm_extraction_failed"],
                metadata={"source_file": source.name, "llm_extraction_failed": True},
            )

    suffix = source.suffix.lower()
    if suffix in {".csv", ".xlsx", ".xls"}:
        if suffix in {".xlsx", ".xls"}:
            spec_items = _ingest_integration_spec(source, item_tags)
            if spec_items:
                return spec_items
        return _ingest_tabular(source, category, item_tags)
    if suffix in {".txt", ".md", ".json"}:
        content = source.read_text(encoding="utf-8")
    elif suffix == ".docx":
        content = _read_docx_text(source)
    elif suffix == ".pdf":
        content = _read_pdf_text(source)
    else:
        raise ValueError(f"Unsupported knowledge file format: {source.suffix}")

    if not content.strip():
        return []
    return [
        add_knowledge_item(
            title=source.stem,
            content=content,
            category=category,
            tags=item_tags,
            metadata={"source_file": source.name},
        )
    ]
