from pathlib import Path
from typing import Any

import pandas as pd

from app.config import GENERATED_DIR
from app.models.schema import FieldMapping, MappingStatus
from app.services.knowledge_base import add_knowledge_item
from app.services.mapping_validator import split_source_expression


REVIEW_COLUMNS = [
    "target_field",
    "suggested_source_field",
    "confirmed_source_field",
    "confidence",
    "status",
    "review_decision",
    "rule_type",
    "reason",
    "review_note",
]


def mappings_to_review_dataframe(mappings: list[FieldMapping]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for mapping in mappings:
        display_source = " + ".join(mapping.source_fields) if mapping.source_fields else mapping.source_field or ""
        rows.append(
            {
                "target_field": mapping.target_field,
                "suggested_source_field": display_source,
                "confirmed_source_field": display_source,
                "confidence": mapping.confidence,
                "status": mapping.status.value,
                "review_decision": "confirm" if display_source or mapping.fixed_value is not None else "unmatched",
                "rule_type": mapping.rule_type.value,
                "reason": mapping.reason,
                "review_note": "",
            }
        )
    return pd.DataFrame(rows, columns=REVIEW_COLUMNS)


def export_mapping_review_excel(mappings: list[FieldMapping], path: str | Path | None = None) -> Path:
    df = mappings_to_review_dataframe(mappings)
    return export_review_dataframe_excel(df, path)


def export_review_dataframe_excel(review_df: pd.DataFrame, path: str | Path | None = None) -> Path:
    target = Path(path) if path else GENERATED_DIR / "mapping_review.xlsx"
    target.parent.mkdir(parents=True, exist_ok=True)
    df = review_df.copy()
    need_review = df[df["status"] == MappingStatus.NEED_REVIEW.value]
    unmatched = df[df["status"] == MappingStatus.UNMATCHED.value]
    rag_evidence = df[df["reason"].str.contains("RAG|DeepSeek", case=False, na=False)]

    with pd.ExcelWriter(target, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="All mappings", index=False)
        need_review.to_excel(writer, sheet_name="Need review", index=False)
        unmatched.to_excel(writer, sheet_name="Unmatched", index=False)
        rag_evidence.to_excel(writer, sheet_name="RAG evidence", index=False)
    return target


def persist_confirmed_mappings(
    review_df: pd.DataFrame,
    tags: list[str] | None = None,
    valid_source_fields: set[str] | None = None,
) -> int:
    """Persist confirmed review decisions as historical_mapping RAG items."""
    item_tags = tags or ["review_confirmed"]
    saved = 0
    for _, row in review_df.iterrows():
        decision = str(row.get("review_decision", "")).strip().lower()
        target_field = str(row.get("target_field", "")).strip()
        confirmed_source = str(row.get("confirmed_source_field", "")).strip()
        if decision not in {"confirm", "confirmed", "approve", "approved", "modify", "modified"}:
            continue
        if not target_field or not confirmed_source:
            continue
        source_fields = split_source_expression(confirmed_source)
        if valid_source_fields is not None:
            source_fields = [field for field in source_fields if field in valid_source_fields]
            if not source_fields:
                continue
        add_knowledge_item(
            title=target_field,
            content=(
                f"target_field: {target_field}\n"
                f"source_fields: {', '.join(source_fields)}\n"
                f"review_note: {row.get('review_note', '')}\n"
                f"original_reason: {row.get('reason', '')}"
            ),
            category="historical_mapping",
            tags=item_tags,
            metadata={
                "target_field": target_field,
                "source_fields": source_fields,
                "review_decision": decision,
                "review_note": str(row.get("review_note", "")),
                "suggested_source_field": str(row.get("suggested_source_field", "")),
                "human_confirmed": True,
            },
        )
        saved += 1
    return saved
