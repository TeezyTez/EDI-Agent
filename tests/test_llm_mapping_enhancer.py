import json

from app.models.schema import FieldMapping, FieldSchema, MappingStatus
from app.services.knowledge_base import add_knowledge_item
from app.services.llm_mapping_enhancer import apply_knowledge_hints, enhance_mappings_with_deepseek


def test_deepseek_confidence_replaces_rule_confidence(monkeypatch):
    monkeypatch.setattr(
        "app.services.llm_mapping_enhancer._call_deepseek",
        lambda messages: {
            "mapping_type": "direct",
            "source_fields": ["GFBL.BL_NO"],
            "confidence": 0.2,
            "needs_review": True,
            "reason": "Not a credible match.",
        },
    )
    monkeypatch.setattr("app.services.llm_mapping_enhancer._knowledge_for_target", lambda target: [])

    mappings = [
        FieldMapping(
            source_field="GFBL.BL_NO",
            source_fields=["GFBL.BL_NO"],
            target_field="filingPartyName",
            confidence=0.82,
            reason="rule score",
            status=MappingStatus.NEED_REVIEW,
        )
    ]
    sources = [FieldSchema(field_name="GFBL.BL_NO", description="Bill of lading number", type="string")]
    targets = [FieldSchema(field_name="filingPartyName", description="Filing party name", type="string")]

    enhanced, _ = enhance_mappings_with_deepseek(mappings, sources, targets)

    assert enhanced[0].confidence == 0.2
    assert enhanced[0].status == MappingStatus.UNMATCHED
    assert enhanced[0].source_fields == []


def test_deepseek_candidate_pool_survives_fixed_value_response(monkeypatch):
    prompts = []

    def fake_call(messages):
        payload = json.loads(messages[-1]["content"])
        prompts.append(payload)
        target_name = payload["target_api_field"]["field_name"]
        if target_name == "filingPartyName":
            return {
                "mapping_type": "fixed_value",
                "source_fields": [],
                "fixed_value": "STAR CONCORD LOGISTICS L.L.C",
                "confidence": 0.95,
                "needs_review": False,
                "reason": "Fixed platform filing party.",
            }
        return {
            "mapping_type": "direct",
            "source_fields": ["GFBL.BL_NO"],
            "confidence": 0.93,
            "needs_review": False,
            "reason": "Bill of lading number.",
        }

    monkeypatch.setattr("app.services.llm_mapping_enhancer._call_deepseek", fake_call)
    monkeypatch.setattr("app.services.llm_mapping_enhancer._knowledge_for_target", lambda target: [])

    mappings = [
        FieldMapping(
            source_field=None,
            target_field="filingPartyName",
            confidence=0.1,
            reason="rule score",
            status=MappingStatus.UNMATCHED,
        ),
        FieldMapping(
            source_field="GFBL.BL_NO",
            source_fields=["GFBL.BL_NO"],
            target_field="blNo",
            confidence=0.8,
            reason="rule score",
            status=MappingStatus.NEED_REVIEW,
        ),
    ]
    sources = [
        FieldSchema(field_name="GFBL.BL_NO", description="Bill of lading number", type="string"),
        FieldSchema(field_name="GFBL.VSL", description="Vessel name", type="string"),
    ]
    targets = [
        FieldSchema(field_name="filingPartyName", description="Filing party name", type="string"),
        FieldSchema(field_name="blNo", description="Bill of lading number", type="string"),
    ]

    enhanced, _ = enhance_mappings_with_deepseek(mappings, sources, targets)

    assert prompts[0]["candidate_database_fields"]
    assert prompts[1]["candidate_database_fields"]
    assert enhanced[0].fixed_value == "STAR CONCORD LOGISTICS L.L.C"
    assert enhanced[1].source_fields == ["GFBL.BL_NO"]


def test_apply_knowledge_hints_matches_array_paths_and_source_aliases():
    add_knowledge_item(
        title="equipmentDetails.equipmentNumber",
        category="historical_mapping",
        content="Direct mapping from GFBLCNT.CNT_NO",
        metadata={"target_field": "equipmentDetails.equipmentNumber", "source_fields": ["GFBLCNT.CNT_NO"]},
    )

    mappings = [
        FieldMapping(
            source_field=None,
            target_field="equipmentDetails[].equipmentNumber",
            confidence=0.4,
            reason="rule score",
            status=MappingStatus.UNMATCHED,
        )
    ]
    sources = [FieldSchema(field_name="GFBLCNT.CTN_NO", description="Container number", type="string")]
    targets = [FieldSchema(field_name="equipmentDetails[].equipmentNumber", description="Container number", type="string")]

    enhanced, message = apply_knowledge_hints(mappings, sources, targets)

    assert "RAG applied 1" in message
    assert enhanced[0].source_fields == ["GFBLCNT.CTN_NO"]
    assert enhanced[0].status == MappingStatus.NEED_REVIEW


def test_apply_knowledge_hints_matches_nested_suffix_paths_and_fixed_values():
    add_knowledge_item(
        title="items.hsCode",
        category="historical_mapping",
        content="Direct mapping from GFBL.HS_CD",
        metadata={"target_field": "items.hsCode", "source_fields": ["GFBL.HS_CD"]},
    )
    add_knowledge_item(
        title="forwardingAgentPartyDetails.country",
        category="fixed_value_rule",
        content="Fixed value AE",
        metadata={"target_field": "forwardingAgentPartyDetails.country", "source_fields": [], "fixed_value": "AE"},
    )

    mappings = [
        FieldMapping(
            source_field=None,
            target_field="equipmentDetails[].items[].hsCode",
            confidence=0.4,
            reason="rule score",
            status=MappingStatus.UNMATCHED,
        ),
        FieldMapping(
            source_field=None,
            target_field="forwardingAgentPartyDetails[].country",
            confidence=0.2,
            reason="rule score",
            status=MappingStatus.UNMATCHED,
        ),
    ]
    sources = [FieldSchema(field_name="GFBL.HS_CD", description="HS code", type="string")]
    targets = [
        FieldSchema(field_name="equipmentDetails[].items[].hsCode", description="HS code", type="string"),
        FieldSchema(field_name="forwardingAgentPartyDetails[].country", description="Forwarder country", type="string"),
    ]

    enhanced, message = apply_knowledge_hints(mappings, sources, targets)

    assert "RAG applied 2" in message
    assert enhanced[0].source_fields == ["GFBL.HS_CD"]
    assert enhanced[1].fixed_value == "AE"
    assert enhanced[1].status == MappingStatus.AUTO_CONFIRMED
