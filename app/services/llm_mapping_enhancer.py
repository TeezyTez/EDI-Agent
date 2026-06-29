import json
from typing import Any

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, LLM_CANDIDATE_LIMIT
from app.models.schema import FieldMapping, FieldSchema, MappingStatus
from app.services.field_matcher import score_fields
from app.services.knowledge_base import list_knowledge_items, search_knowledge


SYSTEM_PROMPT = """You are an enterprise EDI/API integration mapping expert.
Map target API fields to source database columns.
Return strict JSON only. Do not include markdown.
Use null when there is no credible source column.
Prefer business semantics over exact string matching, but do not invent fields.
Use retrieved business knowledge and historical mappings when they are relevant."""


def _knowledge_for_target(target: FieldSchema, limit: int = 5) -> list[dict[str, Any]]:
    query = f"{target.field_name} {target.description} {target.type}"
    exact = [item for item in list_knowledge_items() if item.metadata.get("target_field") == target.field_name]
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


def _top_candidates(
    target: FieldSchema,
    sources: list[FieldSchema],
    limit: int,
    knowledge_source_fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    scored: list[tuple[float, FieldSchema, str]] = []
    for source in sources:
        score, reason = score_fields(source, target)
        scored.append((score, source, reason))
    scored.sort(key=lambda item: item[0], reverse=True)
    by_name = {source.field_name: source for source in sources}
    selected: list[tuple[float, FieldSchema, str]] = []
    for field_name in knowledge_source_fields or []:
        source = by_name.get(field_name)
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
            "source_field": "string or null",
            "confidence": "number between 0 and 1",
            "reason": "short mapping reason",
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def apply_knowledge_hints(
    mappings: list[FieldMapping],
    source_fields: list[FieldSchema],
    target_fields: list[FieldSchema],
) -> tuple[list[FieldMapping], str]:
    """Apply explicit RAG mapping hints before LLM calls."""
    source_names = {field.field_name for field in source_fields}
    targets_by_name = {field.field_name: field for field in target_fields}
    enhanced: list[FieldMapping] = []
    applied = 0

    for mapping in mappings:
        target = targets_by_name[mapping.target_field]
        knowledge = _knowledge_for_target(target)
        exact_sources: list[str] = []
        for item in knowledge:
            metadata = item.get("metadata") or {}
            if metadata.get("target_field") != target.field_name:
                continue
            for source_field in metadata.get("source_fields") or []:
                if source_field in source_names and source_field not in exact_sources:
                    exact_sources.append(source_field)
        if exact_sources:
            applied += 1
            display_source = " + ".join(exact_sources)
            enhanced.append(
                FieldMapping(
                    source_field=display_source,
                    target_field=mapping.target_field,
                    confidence=max(mapping.confidence, 0.88),
                    reason=(
                        f"RAG explicit mapping hint: {target.field_name} -> "
                        f"{', '.join(exact_sources)}; rule_baseline=({mapping.reason})"
                    ),
                    rule_type=mapping.rule_type,
                    status=MappingStatus.NEED_REVIEW,
                )
            )
        else:
            enhanced.append(mapping)
    return enhanced, f"RAG applied {applied} explicit mapping hints."


def _call_deepseek(messages: list[dict[str, str]]) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package is not installed. Run `pip install -r requirements.txt`.") from exc

    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured.")

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    completion = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content or "{}"
    return json.loads(content)


def enhance_mappings_with_deepseek(
    mappings: list[FieldMapping],
    source_fields: list[FieldSchema],
    target_fields: list[FieldSchema],
    max_targets: int | None = None,
) -> tuple[list[FieldMapping], str]:
    """Use DeepSeek to re-rank low-confidence API-to-database mappings."""
    targets_by_name = {field.field_name: field for field in target_fields}
    source_names = {field.field_name for field in source_fields}
    enhanced: list[FieldMapping] = []
    processed = 0

    for mapping in mappings:
        if mapping.status == MappingStatus.AUTO_CONFIRMED:
            enhanced.append(mapping)
            continue
        if max_targets is not None and processed >= max_targets:
            enhanced.append(mapping)
            continue

        target = targets_by_name[mapping.target_field]
        knowledge = _knowledge_for_target(target)
        candidates = _top_candidates(target, source_fields, LLM_CANDIDATE_LIMIT, _knowledge_source_fields(knowledge))
        response = _call_deepseek(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(target, candidates, knowledge)},
            ]
        )
        processed += 1

        source_field = response.get("source_field")
        confidence = float(response.get("confidence") or 0)
        reason = str(response.get("reason") or "DeepSeek semantic mapping.")
        if source_field not in source_names:
            enhanced.append(mapping)
            continue

        if confidence >= 0.90:
            status = MappingStatus.AUTO_CONFIRMED
        elif confidence >= 0.70:
            status = MappingStatus.NEED_REVIEW
        else:
            status = MappingStatus.UNMATCHED
            source_field = None

        enhanced.append(
            FieldMapping(
                source_field=source_field,
                target_field=mapping.target_field,
                confidence=max(mapping.confidence, min(confidence, 1.0)),
                reason=f"DeepSeek+RAG: {reason}; knowledge_items={len(knowledge)}; rule_baseline=({mapping.reason})",
                rule_type=mapping.rule_type,
                status=status,
            )
        )

    return enhanced, f"DeepSeek enhanced {processed} low-confidence mappings with RAG context."
