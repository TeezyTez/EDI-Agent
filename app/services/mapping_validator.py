import re

from app.models.schema import FieldMapping, MappingStatus


SOURCE_SPLIT_PATTERN = re.compile(r"\s*(?:\+|,|;|\n)\s*")


def split_source_expression(source_field: str | None) -> list[str]:
    if not source_field:
        return []
    return [part.strip() for part in SOURCE_SPLIT_PATTERN.split(source_field) if part.strip()]


def validate_mappings_against_source_schema(
    mappings: list[FieldMapping],
    valid_source_fields: set[str],
) -> tuple[list[FieldMapping], int]:
    """Reject mappings that reference source fields not present in the database schema."""
    validated: list[FieldMapping] = []
    invalid_count = 0
    for mapping in mappings:
        source_parts = mapping.source_fields or split_source_expression(mapping.source_field)
        invalid_parts = [part for part in source_parts if part not in valid_source_fields]
        if invalid_parts:
            invalid_count += 1
            validated.append(
                FieldMapping(
                    source_field=None,
                    source_fields=[],
                    target_field=mapping.target_field,
                    confidence=min(mapping.confidence, 0.69),
                    reason=(
                        f"Rejected invalid source fields not found in database schema: "
                        f"{', '.join(invalid_parts)}; original=({mapping.reason})"
                    ),
                    rule_type=mapping.rule_type,
                    fixed_value=mapping.fixed_value,
                    transform_expression=mapping.transform_expression,
                    status=MappingStatus.UNMATCHED,
                )
            )
        else:
            validated.append(mapping)
    return validated, invalid_count
