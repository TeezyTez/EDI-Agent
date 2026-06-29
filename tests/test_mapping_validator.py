from app.models.schema import FieldMapping, MappingStatus
from app.services.mapping_validator import split_source_expression, validate_mappings_against_source_schema


def test_split_source_expression_handles_composite_sources():
    assert split_source_expression("GFBL.MBL_NO + GFBLCNT.CTN_NO, GFBL.JOB_NO") == [
        "GFBL.MBL_NO",
        "GFBLCNT.CTN_NO",
        "GFBL.JOB_NO",
    ]


def test_validate_mappings_rejects_sources_not_in_database_schema():
    mappings = [
        FieldMapping(
            source_field="GFBL.JOB_NO + FAKE.FIELD",
            target_field="job",
            confidence=0.88,
            reason="RAG",
            status=MappingStatus.NEED_REVIEW,
        )
    ]

    validated, invalid_count = validate_mappings_against_source_schema(mappings, {"GFBL.JOB_NO"})

    assert invalid_count == 1
    assert validated[0].source_field is None
    assert validated[0].status == MappingStatus.UNMATCHED
