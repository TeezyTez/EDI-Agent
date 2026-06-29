from app.services.llm_knowledge_extractor import _safe_json_loads


def test_safe_json_loads_returns_fallback_for_truncated_json():
    payload = _safe_json_loads('{"items": [{"title": "broken", "content": "unterminated]')

    assert payload["items"][0]["metadata"]["llm_parse_failed"] is True


def test_safe_json_loads_extracts_json_object_from_wrapped_text():
    payload = _safe_json_loads('prefix {"items": []} suffix')

    assert payload == {"items": []}
