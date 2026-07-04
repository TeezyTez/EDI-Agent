from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import re
from typing import Any

from app.config import (
    CACHE_DIR,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MAX_WORKERS,
    DEEPSEEK_MODEL,
    DEEPSEEK_TIMEOUT_SECONDS,
    LLM_CANDIDATE_LIMIT,
)
from app.models.schema import FieldMapping, FieldSchema, MappingStatus, RuleType
from app.services.field_matcher import expanded_tokens, score_fields
from app.services.knowledge_base import list_knowledge_items, search_knowledge


SYSTEM_PROMPT = """You are an enterprise EDI/API integration mapping expert.
Map target API fields to source database columns and transformation rules.
Return strict JSON only. Do not include markdown.
Use an empty source_fields list when there is no credible source column.
Prefer business semantics over exact string matching, but do not invent fields.
Only use source fields from candidate_database_fields.
Use retrieved business knowledge and historical mappings when they are relevant."""


def _knowledge_for_target(target: FieldSchema, limit: int = 5) -> list[dict[str, Any]]:
    query = f"{target.field_name} {target.description} {target.type}"
    exact = [
        item
        for item in list_knowledge_items()
        if _target_field_matches(target.field_name, item.metadata.get("target_field"))
    ]
    fuzzy = search_knowledge(query, limit=limit)
    merged = []
    seen: set[str] = set()
    for item in [*exact, *fuzzy]:
        if item.id in seen:
            continue
        seen.add(item.id)
        merged.append(item)
        if len(merged) >= limit:
            break
    return [
        {
            "title": item.title,
            "category": item.category,
            "content": item.content[:1200],
            "tags": item.tags,
            "metadata": item.metadata,
        }
        for item in merged
    ]


def _knowledge_source_fields(knowledge: list[dict[str, Any]]) -> list[str]:
    fields: list[str] = []
    for item in knowledge:
        metadata = item.get("metadata") or {}
        for field in metadata.get("source_fields") or []:
            if field not in fields:
                fields.append(field)
    return fields


def _normalize_target_path(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("[]", "")
    text = re.sub(r"[^a-z0-9_.]+", "", text)
    return re.sub(r"\.+", ".", text).strip(".")


def _target_field_matches(target_field: str, knowledge_target: Any) -> bool:
    knowledge_path = _normalize_target_path(knowledge_target)
    target_path = _normalize_target_path(target_field)
    if not knowledge_path or not target_path:
        return False
    if knowledge_path == target_path:
        return True
    if "." in knowledge_path and target_path.endswith(f".{knowledge_path}"):
        return True
    if "." in target_path and knowledge_path.endswith(f".{target_path}"):
        return True
    return False


def _source_hint_variants(source_field: str) -> list[str]:
    variants = [source_field]
    replacements = [
        ("CFBLCNT.", "GFBLCNT."),
        (".CNT_", ".CTN_"),
        (".CTN_", ".CNT_"),
    ]
    for old, new in replacements:
        if old in source_field:
            variants.append(source_field.replace(old, new))
    for current in list(variants):
        for old, new in replacements:
            if old in current:
                variants.append(current.replace(old, new))
    deduped: list[str] = []
    for variant in variants:
        if variant not in deduped:
            deduped.append(variant)
    return deduped


def _resolve_source_hint(source_field: str, sources_by_name: dict[str, FieldSchema]) -> FieldSchema | None:
    for variant in _source_hint_variants(source_field.strip()):
        source = sources_by_name.get(variant)
        if source:
            return source

    lowered = source_field.lower()
    by_lower = {name.lower(): source for name, source in sources_by_name.items()}
    for variant in _source_hint_variants(lowered):
        source = by_lower.get(variant)
        if source:
            return source

    raw_column = lowered.split(".")[-1].replace(" ", "").replace("_", "")
    for source_name, source in sources_by_name.items():
        column = source_name.split(".")[-1].lower().replace(" ", "").replace("_", "")
        if column == raw_column:
            return source
    return None


def _top_candidates(
    target: FieldSchema,
    sources: list[FieldSchema],
    limit: int,
    knowledge_source_fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    scored: list[tuple[float, FieldSchema, str]] = []
    target_tokens = expanded_tokens(target.field_name) | expanded_tokens(target.description)
    for source in sources:
        score, reason = score_fields(source, target)
        source_tokens = expanded_tokens(source.field_name) | expanded_tokens(source.description)
        token_score = len(source_tokens & target_tokens) / len(source_tokens | target_tokens) if source_tokens and target_tokens else 0.0
        boost = min(token_score * 0.25, 0.15)
        scored.append((min(score + boost, 1.0), source, f"{reason}, token_recall={token_score:.2f}"))
    scored.sort(key=lambda item: item[0], reverse=True)
    by_name = {source.field_name: source for source in sources}
    selected: list[tuple[float, FieldSchema, str]] = []
    for field_name in knowledge_source_fields or []:
        source = _resolve_source_hint(field_name, by_name)
        if source:
            score, reason = score_fields(source, target)
            selected.append((score, source, f"RAG explicit candidate; {reason}"))
    for item in scored:
        if item[1].field_name not in {selected_item[1].field_name for selected_item in selected}:
            selected.append(item)
        if len(selected) >= limit:
            break
    return [
        {
            "field_name": source.field_name,
            "description": source.description,
            "type": source.type,
            "required": source.required,
            "rule_score": score,
            "rule_reason": reason,
        }
        for score, source, reason in selected[:limit]
    ]


def _build_user_prompt(target: FieldSchema, candidates: list[dict[str, Any]], knowledge: list[dict[str, Any]]) -> str:
    payload = {
        "target_api_field": {
            "field_name": target.field_name,
            "description": target.description,
            "type": target.type,
            "required": target.required,
            "example": target.example,
        },
        "candidate_database_fields": candidates,
        "retrieved_business_knowledge": knowledge,
        "response_schema": {
            "mapping_type": "direct | merge | split | enum_mapping | fixed_value | date_format | unmatched",
            "source_fields": ["zero, one, or more exact field_name values from candidate_database_fields"],
            "fixed_value": "optional fixed/default value when mapping_type is fixed_value",
            "transform_expression": "optional concise transformation instruction",
            "confidence": "number between 0 and 1",
            "needs_review": "boolean",
            "reason": "short mapping reason",
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _rule_type_from_mapping_type(value: Any) -> RuleType:
    text = str(value or "").strip().lower()
    aliases = {
        "direct": RuleType.DIRECT,
        "merge": RuleType.MERGE,
        "split": RuleType.SPLIT,
        "enum_mapping": RuleType.ENUM_MAPPING,
        "enum": RuleType.ENUM_MAPPING,
        "fixed_value": RuleType.DEFAULT_VALUE,
        "default_value": RuleType.DEFAULT_VALUE,
        "date_format": RuleType.DATE_FORMAT,
        "date": RuleType.DATE_FORMAT,
    }
    return aliases.get(text, RuleType.DIRECT)


def _normalize_response_sources(response: dict[str, Any]) -> list[str]:
    raw_sources = response.get("source_fields")
    if raw_sources is None:
        raw_sources = [response.get("source_field")]
    if isinstance(raw_sources, str):
        raw_sources = [raw_sources]
    if not isinstance(raw_sources, list):
        return []
    sources: list[str] = []
    for source in raw_sources:
        text = str(source or "").strip()
        if text and text.lower() not in {"null", "none", "n/a", "unmatched"} and text not in sources:
            sources.append(text)
    return sources


def _resolve_source_field(raw_source: str, source_names: set[str], candidates: list[dict[str, Any]]) -> str | None:
    if raw_source in source_names:
        return raw_source
    lowered = raw_source.lower()
    for source_name in source_names:
        if source_name.lower() == lowered:
            return source_name

    candidate_names = [str(candidate.get("field_name") or "") for candidate in candidates]
    search_order = [*candidate_names, *[name for name in source_names if name not in candidate_names]]
    resolved_hint = _resolve_source_hint(
        raw_source,
        {source_name: FieldSchema(field_name=source_name) for source_name in search_order},
    )
    if resolved_hint:
        return resolved_hint.field_name

    raw_column = lowered.split(".")[-1].replace(" ", "").replace("_", "")
    if not raw_column:
        return None
    matches = []
    for source_name in search_order:
        column = source_name.split(".")[-1].lower().replace(" ", "").replace("_", "")
        if column == raw_column:
            matches.append(source_name)
    return matches[0] if matches else None


def _status_from_llm(confidence: float, source_fields: list[str], fixed_value: Any, needs_review: bool) -> MappingStatus:
    if not source_fields and fixed_value in (None, ""):
        return MappingStatus.UNMATCHED
    if confidence >= 0.90 and not needs_review:
        return MappingStatus.AUTO_CONFIRMED
    if confidence >= 0.70:
        return MappingStatus.NEED_REVIEW
    return MappingStatus.UNMATCHED


def apply_knowledge_hints(
    mappings: list[FieldMapping],
    source_fields: list[FieldSchema],
    target_fields: list[FieldSchema],
) -> tuple[list[FieldMapping], str]:
    """Apply explicit RAG mapping hints before LLM calls."""
    sources_by_name = {field.field_name: field for field in source_fields}
    targets_by_name = {field.field_name: field for field in target_fields}
    enhanced: list[FieldMapping] = []
    applied = 0

    for mapping in mappings:
        target = targets_by_name[mapping.target_field]
        knowledge = _knowledge_for_target(target)
        exact_sources: list[str] = []
        fixed_value = None
        transform_expression = None
        matched_knowledge_targets: list[str] = []
        for item in knowledge:
            metadata = item.get("metadata") or {}
            if not _target_field_matches(target.field_name, metadata.get("target_field")):
                continue
            matched_knowledge_targets.append(str(metadata.get("target_field") or item.get("title") or ""))
            for source_field in metadata.get("source_fields") or []:
                source = _resolve_source_hint(str(source_field), sources_by_name)
                if source and source.field_name not in exact_sources:
                    exact_sources.append(source.field_name)
            if fixed_value in (None, "") and metadata.get("fixed_value") not in (None, ""):
                fixed_value = metadata.get("fixed_value")
            if transform_expression in (None, "") and metadata.get("transform_rule"):
                transform_expression = str(metadata.get("transform_rule"))
        if exact_sources:
            applied += 1
            display_source = " + ".join(exact_sources)
            rule_type = RuleType.MERGE if len(exact_sources) > 1 else mapping.rule_type
            if transform_expression and len(exact_sources) == 1:
                rule_type = RuleType.ENUM_MAPPING if "mapping" in transform_expression.lower() else mapping.rule_type
            enhanced.append(
                FieldMapping(
                    source_field=display_source,
                    source_fields=exact_sources,
                    target_field=mapping.target_field,
                    confidence=max(mapping.confidence, 0.88),
                    reason=(
                        f"RAG explicit mapping hint: {target.field_name} -> "
                        f"{', '.join(exact_sources)}; knowledge_target=({', '.join(matched_knowledge_targets)}); "
                        f"rule_baseline=({mapping.reason})"
                    ),
                    rule_type=rule_type,
                    transform_expression=transform_expression,
                    status=MappingStatus.NEED_REVIEW,
                )
            )
        elif fixed_value not in (None, ""):
            applied += 1
            enhanced.append(
                FieldMapping(
                    source_field=None,
                    source_fields=[],
                    target_field=mapping.target_field,
                    confidence=max(mapping.confidence, 0.95),
                    reason=(
                        f"RAG fixed value hint: {target.field_name} = {fixed_value}; "
                        f"knowledge_target=({', '.join(matched_knowledge_targets)}); "
                        f"rule_baseline=({mapping.reason})"
                    ),
                    rule_type=RuleType.DEFAULT_VALUE,
                    fixed_value=fixed_value,
                    transform_expression=transform_expression,
                    status=MappingStatus.AUTO_CONFIRMED,
                )
            )
        else:
            enhanced.append(mapping)
    return enhanced, f"RAG applied {applied} explicit mapping hints."


def _deepseek_cache_path(messages: list[dict[str, str]]) -> Any:
    payload = {
        "base_url": DEEPSEEK_BASE_URL,
        "model": DEEPSEEK_MODEL,
        "messages": messages,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return CACHE_DIR / f"deepseek_mapping_{digest}.json"


def _json_fingerprint(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _fields_fingerprint(fields: list[FieldSchema]) -> str:
    return _json_fingerprint([field.model_dump(mode="json") for field in fields])


def _mappings_fingerprint(mappings: list[FieldMapping]) -> str:
    return _json_fingerprint([mapping.model_dump(mode="json") for mapping in mappings])


def _knowledge_fingerprint() -> str:
    return _json_fingerprint(
        [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "content": item.content,
                "tags": item.tags,
                "metadata": item.metadata,
            }
            for item in list_knowledge_items()
        ]
    )


def _enhancement_cache_path(
    mappings: list[FieldMapping],
    source_fields: list[FieldSchema],
    target_fields: list[FieldSchema],
    max_targets: int | None,
    candidate_limit: int,
) -> Any:
    digest = _json_fingerprint(
        {
            "base_url": DEEPSEEK_BASE_URL,
            "model": DEEPSEEK_MODEL,
            "candidate_limit": candidate_limit,
            "max_targets": max_targets,
            "source_fields": _fields_fingerprint(source_fields),
            "target_fields": _fields_fingerprint(target_fields),
            "input_mappings": _mappings_fingerprint(mappings),
            "knowledge": _knowledge_fingerprint(),
            "version": 2,
        }
    )
    return CACHE_DIR / f"deepseek_enhanced_mappings_{digest}.json"


def _load_enhancement_cache(path: Any) -> tuple[list[FieldMapping], str] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        mappings = [FieldMapping(**item) for item in payload.get("mappings") or []]
        message = str(payload.get("message") or "DeepSeek mapping cache hit.")
        if mappings:
            return mappings, f"{message} (cached)"
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None
    return None


def _write_enhancement_cache(path: Any, mappings: list[FieldMapping], message: str) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "message": message,
                    "mappings": [mapping.model_dump(mode="json") for mapping in mappings],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass


def _call_deepseek(messages: list[dict[str, str]]) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package is not installed. Run `pip install -r requirements.txt`.") from exc

    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured.")

    cache_path = _deepseek_cache_path(messages)
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=DEEPSEEK_TIMEOUT_SECONDS)
    completion = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content or "{}"
    response = json.loads(content)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass
    return response


def _clone_mapping(mapping: FieldMapping, **updates: Any) -> FieldMapping:
    payload = mapping.model_dump()
    payload.update(updates)
    return FieldMapping(**payload)


def _safe_float(value: Any, fallback: float) -> float:
    try:
        return max(0.0, min(float(value), 1.0))
    except (TypeError, ValueError):
        return fallback


def _safe_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _mapping_with_deepseek_error(mapping: FieldMapping, exc: Exception) -> FieldMapping:
    message = str(exc).strip().replace("\n", " ")
    if len(message) > 180:
        message = f"{message[:177]}..."
    return _clone_mapping(mapping, reason=f"{mapping.reason}; DeepSeek skipped: {type(exc).__name__}: {message}")


def _mapping_from_deepseek_response(
    mapping: FieldMapping,
    response: dict[str, Any],
    knowledge: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    source_names: set[str],
) -> FieldMapping:
    response_sources = _normalize_response_sources(response)
    resolved_source_fields: list[str] = []
    for raw_source in response_sources:
        resolved = _resolve_source_field(raw_source, source_names, candidates)
        if resolved and resolved not in resolved_source_fields:
            resolved_source_fields.append(resolved)

    if response_sources and not resolved_source_fields:
        return _clone_mapping(
            mapping,
            reason=f"{mapping.reason}; DeepSeek returned source fields outside candidate list: {', '.join(response_sources)}",
        )

    confidence = _safe_float(response.get("confidence"), mapping.confidence)
    reason = str(response.get("reason") or "DeepSeek semantic mapping.")
    rule_type = _rule_type_from_mapping_type(response.get("mapping_type"))
    fixed_value = response.get("fixed_value")
    transform_expression = _safe_text(response.get("transform_expression"))
    needs_review = bool(response.get("needs_review", confidence < 0.9))

    status = _status_from_llm(confidence, resolved_source_fields, fixed_value, needs_review)
    if status == MappingStatus.UNMATCHED and not fixed_value:
        resolved_source_fields = []
    display_source = " + ".join(resolved_source_fields) if resolved_source_fields else None

    return FieldMapping(
        source_field=display_source,
        source_fields=resolved_source_fields,
        target_field=mapping.target_field,
        confidence=confidence,
        reason=(
            f"DeepSeek+RAG: {reason}; mapping_type={response.get('mapping_type') or rule_type.value}; "
            f"knowledge_items={len(knowledge)}; candidates={len(candidates)}; "
            f"rule_baseline=({mapping.reason})"
        ),
        rule_type=rule_type,
        fixed_value=fixed_value,
        transform_expression=transform_expression,
        status=status,
    )


def enhance_mappings_with_deepseek(
    mappings: list[FieldMapping],
    source_fields: list[FieldSchema],
    target_fields: list[FieldSchema],
    max_targets: int | None = None,
) -> tuple[list[FieldMapping], str]:
    """Use DeepSeek as a mapping decision node over a wider candidate set."""
    database_fields = source_fields
    targets_by_name = {field.field_name: field for field in target_fields}
    source_names = {field.field_name for field in database_fields}
    candidate_limit = max(LLM_CANDIDATE_LIMIT, 20)
    enhancement_cache_path = _enhancement_cache_path(mappings, database_fields, target_fields, max_targets, candidate_limit)
    cached_enhancement = _load_enhancement_cache(enhancement_cache_path)
    if cached_enhancement:
        return cached_enhancement

    results: list[FieldMapping | None] = [None] * len(mappings)
    work_items: list[tuple[int, FieldMapping]] = []

    for index, mapping in enumerate(mappings):
        if max_targets is not None and len(work_items) >= max_targets:
            results[index] = mapping
            continue
        work_items.append((index, mapping))

    def decide(item: tuple[int, FieldMapping]) -> tuple[int, FieldMapping, Exception | None]:
        index, mapping = item
        target = targets_by_name[mapping.target_field]
        try:
            knowledge = _knowledge_for_target(target)
            candidates = _top_candidates(target, database_fields, candidate_limit, _knowledge_source_fields(knowledge))
            response = _call_deepseek(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(target, candidates, knowledge)},
                ]
            )
            return index, _mapping_from_deepseek_response(mapping, response, knowledge, candidates, source_names), None
        except Exception as exc:
            return index, _mapping_with_deepseek_error(mapping, exc), exc

    errors: list[Exception] = []
    worker_count = max(1, min(DEEPSEEK_MAX_WORKERS, len(work_items))) if work_items else 1
    if worker_count == 1:
        for item in work_items:
            index, mapping, error = decide(item)
            results[index] = mapping
            if error:
                errors.append(error)
    else:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(decide, item) for item in work_items]
            for future in as_completed(futures):
                index, mapping, error = future.result()
                results[index] = mapping
                if error:
                    errors.append(error)

    enhanced = [result if result is not None else mapping for result, mapping in zip(results, mappings, strict=True)]
    success_count = len(work_items) - len(errors)
    message = (
        f"DeepSeek decided {success_count}/{len(work_items)} mappings with RAG context, "
        f"{candidate_limit} candidates per target, and {worker_count} worker(s)."
    )
    if errors:
        message += f" {len(errors)} mapping(s) fell back to rule/RAG results after DeepSeek errors."
    else:
        _write_enhancement_cache(enhancement_cache_path, enhanced, message)
    return enhanced, message
