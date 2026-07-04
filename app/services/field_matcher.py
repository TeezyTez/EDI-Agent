from difflib import SequenceMatcher
import re
from typing import Iterable

from app.config import CONFIDENCE_AUTO_CONFIRM, CONFIDENCE_NEED_REVIEW
from app.models.schema import FieldMapping, FieldSchema, MappingStatus


DOMAIN_ALIASES = {
    "bill_of_lading": {"bl", "b/l", "bill", "lading", "billoflading", "提单", "提單", "提单号", "提單號", "blno", "bl_no"},
    "container": {"container", "cntr", "ctn", "箱号", "箱號", "柜号", "櫃號", "containerno", "container_no"},
    "vessel": {"vessel", "vsl", "船名", "船舶"},
    "voyage": {"voyage", "voy", "航次"},
    "shipper": {"shipper", "发货人", "發貨人", "托运人", "託運人"},
    "consignee": {"consignee", "收货人", "收貨人"},
    "notify": {"notify", "通知人"},
    "party": {"party", "customer", "cust", "客户", "客戶"},
    "port": {"port", "pod", "pol", "locode", "港口", "口岸"},
    "loading": {"loading", "load", "pol", "装货", "裝貨"},
    "unloading": {"unloading", "discharge", "pod", "卸货", "卸貨"},
    "package": {"package", "pkg", "packages", "件数", "件數", "包装", "包裝"},
    "weight": {"weight", "wt", "grossweight", "netweight", "重量"},
    "volume": {"volume", "vol", "measurement", "体积", "體積"},
    "seal": {"seal", "封条", "封條", "铅封", "鉛封"},
    "date": {"date", "dt", "日期"},
    "number": {"number", "num", "no", "nbr", "编号", "編號", "号码", "號碼"},
    "code": {"code", "cd", "代码", "代碼"},
    "type": {"type", "tp", "类型", "類型"},
    "name": {"name", "nm", "名称", "名稱", "姓名"},
    "address": {"address", "addr", "地址"},
    "city": {"city", "城市"},
    "country": {"country", "ctry", "国家", "國家"},
    "currency": {"currency", "curr", "币种", "幣種"},
    "invoice": {"invoice", "inv", "发票", "發票"},
    "job": {"job", "jobno", "job_no", "业务号", "業務號"},
}


def _normalize(value: object) -> str:
    text = "" if value is None else str(value).lower()
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", "" if value is None else str(value)).lower()
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text).strip()


def _ratio(left: object, right: object) -> float:
    return SequenceMatcher(None, _normalize(left), _normalize(right)).ratio()


def _token_overlap(left: str, right: str) -> float:
    left_tokens = set(_normalize(left).split())
    right_tokens = set(_normalize(right).split())
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _tokens(value: object) -> set[str]:
    return set(_normalize(value).split())


def expanded_tokens(value: object) -> set[str]:
    tokens = _tokens(value)
    normalized = _normalize(value).replace(" ", "")
    expanded = set(tokens)
    for canonical, aliases in DOMAIN_ALIASES.items():
        if canonical in tokens or canonical.replace("_", "") in normalized or aliases & tokens or any(alias.replace("/", "") in normalized for alias in aliases):
            expanded.add(canonical)
            expanded.update(aliases)
    return expanded


def _canonical_type(value: str) -> str:
    normalized = _normalize(value).replace(" ", "")
    if not normalized:
        return "string"
    if normalized.startswith("x"):
        return "string"
    if re.fullmatch(r"9+", normalized):
        return "number"
    aliases = {
        "str": "string",
        "string": "string",
        "char": "string",
        "nchar": "string",
        "varchar": "string",
        "nvarchar": "string",
        "text": "string",
        "ntext": "string",
        "uniqueidentifier": "string",
        "int": "number",
        "integer": "number",
        "bigint": "number",
        "smallint": "number",
        "tinyint": "number",
        "float": "number",
        "real": "number",
        "decimal": "number",
        "numeric": "number",
        "money": "number",
        "datetime": "date",
        "datetime2": "date",
        "date": "date",
        "timestamp": "date",
        "bit": "boolean",
        "bool": "boolean",
        "boolean": "boolean",
    }
    return aliases.get(normalized, normalized)


def _type_score(left: str, right: str) -> float:
    return 1.0 if _canonical_type(left) == _canonical_type(right) else 0.0


def _status(confidence: float) -> MappingStatus:
    if confidence >= CONFIDENCE_AUTO_CONFIRM:
        return MappingStatus.AUTO_CONFIRMED
    if confidence >= CONFIDENCE_NEED_REVIEW:
        return MappingStatus.NEED_REVIEW
    return MappingStatus.UNMATCHED


def score_fields(source: FieldSchema, target: FieldSchema) -> tuple[float, str]:
    name_score = _ratio(source.field_name, target.field_name)
    source_name_tokens = expanded_tokens(source.field_name)
    target_name_tokens = expanded_tokens(target.field_name)
    source_all_tokens = source_name_tokens | expanded_tokens(source.description)
    target_all_tokens = target_name_tokens | expanded_tokens(target.description)
    name_token_score = len(source_name_tokens & target_name_tokens) / len(source_name_tokens | target_name_tokens) if source_name_tokens and target_name_tokens else 0.0
    desc_score = max(
        _ratio(source.description, target.description),
        _token_overlap(source.description, target.description),
        len(source_all_tokens & target_all_tokens) / len(source_all_tokens | target_all_tokens) if source_all_tokens and target_all_tokens else 0.0,
    )
    type_score = _type_score(source.type, target.type)
    example_score = _ratio(source.example, target.example)
    confidence = (max(name_score, name_token_score) * 0.45) + (desc_score * 0.25) + (type_score * 0.20) + (example_score * 0.10)
    reason = (
        f"name={name_score:.2f}, name_tokens={name_token_score:.2f}, description={desc_score:.2f}, "
        f"type={type_score:.2f}, example={example_score:.2f}"
    )
    return round(confidence, 4), reason


def generate_mapping_table(source_fields: Iterable[FieldSchema], target_fields: Iterable[FieldSchema]) -> list[FieldMapping]:
    """Match each target field to the best source field using deterministic scores."""
    sources = list(source_fields)
    mappings: list[FieldMapping] = []
    source_tokens = {source.field_name: expanded_tokens(source.field_name) | expanded_tokens(source.description) for source in sources}

    for target in target_fields:
        candidates = []
        target_tokens = expanded_tokens(target.field_name) | expanded_tokens(target.description)
        pool = [source for source in sources if source_tokens[source.field_name] & target_tokens]
        if len(pool) < 25:
            pool = sources

        for source in pool:
            confidence, reason = score_fields(source, target)
            candidates.append((confidence, source, reason))

        if not candidates:
            mappings.append(
                FieldMapping(
                    source_field=None,
                    target_field=target.field_name,
                    confidence=0.0,
                    reason="No available source field.",
                    status=MappingStatus.UNMATCHED,
                )
            )
            continue

        confidence, source, reason = max(candidates, key=lambda item: item[0])
        status = _status(confidence)
        source_name = source.field_name if status != MappingStatus.UNMATCHED else None
        mappings.append(
            FieldMapping(
                source_field=source_name,
                source_fields=[source_name] if source_name else [],
                target_field=target.field_name,
                confidence=confidence,
                reason=reason,
                status=status,
            )
        )
    return mappings
