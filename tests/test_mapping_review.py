import pandas as pd

from app.services.knowledge_base import clear_knowledge_items, search_knowledge
from app.services.mapping_review import export_review_dataframe_excel, persist_confirmed_mappings


def test_persist_confirmed_mappings_saves_historical_mapping(tmp_path):
    clear_knowledge_items()
    review_df = pd.DataFrame(
        [
            {
                "target_field": "genjb_job_number",
                "suggested_source_field": "",
                "confirmed_source_field": "GFBL.JOB_NO",
                "confidence": 0.8,
                "status": "need_review",
                "review_decision": "modify",
                "rule_type": "direct",
                "reason": "manual correction",
                "review_note": "Confirmed by user",
            }
        ]
    )

    saved = persist_confirmed_mappings(review_df, tags=["test"])

    assert saved == 1
    results = search_knowledge("genjb_job_number JOB_NO")
    assert results
    assert results[0].metadata["source_fields"] == ["GFBL.JOB_NO"]


def test_persist_confirmed_mappings_skips_invalid_sources():
    clear_knowledge_items()
    review_df = pd.DataFrame(
        [
            {
                "target_field": "genjb_job_number",
                "suggested_source_field": "",
                "confirmed_source_field": "FAKE.FIELD",
                "confidence": 0.8,
                "status": "need_review",
                "review_decision": "confirm",
                "rule_type": "direct",
                "reason": "manual correction",
                "review_note": "",
            }
        ]
    )

    saved = persist_confirmed_mappings(review_df, valid_source_fields={"GFBL.JOB_NO"})

    assert saved == 0
    assert not search_knowledge("FAKE.FIELD")


def test_export_review_dataframe_excel_creates_workbook(tmp_path):
    path = tmp_path / "mapping_review.xlsx"
    review_df = pd.DataFrame(
        [
            {
                "target_field": "a",
                "suggested_source_field": "b",
                "confirmed_source_field": "b",
                "confidence": 0.9,
                "status": "need_review",
                "review_decision": "confirm",
                "rule_type": "direct",
                "reason": "RAG",
                "review_note": "",
            }
        ]
    )

    output = export_review_dataframe_excel(review_df, path)

    assert output.exists()
