import json
import re
from typing import Any

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, LLM_KNOWLEDGE_CHUNK_CHARS


SYSTEM_PROMPT = """You are an enterprise EDI/API integration knowledge extraction agent.
Extract reusable integration knowledge from arbitrary documents.
Return strict JSON only. Do not include markdown.
Focus on field mappings, fixed values, enum mappings, transformation rules, business terms, and interface constraints.
When a target field maps to source database fields, preserve exact field names such as GFBL.JOB_NO.
When information is uncertain, put it in content and use category business_context instead of inventing a mapping."""


def _chunk_text(text: str, chunk_size: int) -> list[str]:
    clean = text.strip()
    if not clean:
        return []
    return [clean[index : index + chunk_size] for index in range(0, len(clean), chunk_size)]


def _safe_json_loads(content: str) -> dict[str, Any]:
    try:
        return json.loads(content or "{}")
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content or "", flags=re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {
        "items": [
            {
                "title": "Unparsed LLM extraction result",
                "category": "business_context",
                "content": (content or "")[:4000],
                "tags": ["llm_parse_failed"],
                "metadata": {"llm_parse_failed": True},
            }
        ]
    }


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
    return _safe_json_loads(completion.choices[0].message.content or "{}")


def _build_prompt(source_name: str, text: str, default_tags: list[str]) -> str:
    payload = {
        "source_document": source_name,
        "default_tags": default_tags,
        "document_text": text,
        "allowed_categories": [
            "historical_mapping",
            "fixed_value_rule",
            "enum_mapping",
            "transform_rule",
            "field_alias",
            "glossary",
            "business_context",
        ],
        "output_schema": {
            "items": [
                {
                    "title": "short title, preferably target field when available",
                    "category": "one allowed category",
                    "content": "concise reusable knowledge",
                    "tags": ["tag"],
                    "metadata": {
                        "target_field": "optional target API/interface field",
                        "source_fields": ["optional database fields"],
                        "fixed_value": "optional fixed value",
                        "transform_rule": "optional transformation instruction",
                        "enum_map": {"optional_source": "optional_target"},
                    },
                }
            ]
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def extract_knowledge_with_deepseek(source_name: str, text: str, tags: list[str] | None = None) -> list[dict[str, Any]]:
    """Extract structured RAG knowledge items from arbitrary document text."""
    extracted: list[dict[str, Any]] = []
    default_tags = tags or []
    for chunk_index, chunk in enumerate(_chunk_text(text, LLM_KNOWLEDGE_CHUNK_CHARS), start=1):
        response = _call_deepseek(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_prompt(source_name, chunk, default_tags)},
            ]
        )
        for item in response.get("items", []):
            if not isinstance(item, dict):
                continue
            metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
            metadata["source_file"] = source_name
            metadata["llm_extracted"] = True
            metadata["chunk"] = chunk_index
            extracted.append(
                {
                    "title": str(item.get("title") or f"{source_name} chunk {chunk_index}"),
                    "category": str(item.get("category") or "business_context"),
                    "content": str(item.get("content") or ""),
                    "tags": [str(tag) for tag in item.get("tags", []) if str(tag).strip()],
                    "metadata": metadata,
                }
            )
    return extracted
