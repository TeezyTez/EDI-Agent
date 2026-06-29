from difflib import SequenceMatcher
import re
from typing import Iterable

from app.config import CONFIDENCE_AUTO_CONFIRM, CONFIDENCE_NEED_REVIEW
from app.models.schema import FieldMapping, FieldSchema, MappingStatus


def _normalize(value: object) -> str:
    text = "" if value is None else str(value).lower()
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
    desc_score = max(_ratio(source.description, target.description), _token_overlap(source.description, target.description))
    type_score = _type_score(source.type, target.type)
    example_score = _ratio(source.example, target.example)
    confidence = (name_score * 0.45) + (desc_score * 0.25) + (type_score * 0.20) + (example_score * 0.10)
    reason = (
        f"name={name_score:.2f}, description={desc_score:.2f}, "
        f"type={type_score:.2f}, example={example_score:.2f}"
    )
    return round(confidence, 4), reason


def generate_mapping_table(source_fields: Iterable[FieldSchema], target_fields: Iterable[FieldSchema]) -> list[FieldMapping]:
    """Greedily match each target field to the best source field using deterministic scores."""
    sources = list(source_fields)
    mappings: list[FieldMapping] = []
    used_sources: set[str] = set()
    source_tokens = {source.field_name: _tokens(source.field_name) | _tokens(source.description) for source in sources}

    for target in target_fields:
        candidates = []
        target_tokens = _tokens(target.field_name) | _tokens(target.description)
        pool = [
            source
            for source in sources
            if source.field_name not in used_sources and source_tokens[source.field_name] & target_tokens
        ]
        if len(pool) < 25:
            pool = [source for source in sources if source.field_name not in used_sources]

        for source in pool:
            if source.field_name in used_sources:
                continue
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
        if source_name:
            used_sources.add(source_name)
        mappings.append(
            FieldMapping(
                source_field=source_name,
                target_field=target.field_name,
                confidence=confidence,
                reason=reason,
                status=status,
            )
        )
    return mappings
