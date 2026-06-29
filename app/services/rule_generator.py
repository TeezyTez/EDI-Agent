from app.models.schema import FieldMapping, FieldSchema, MappingStatus, RuleType, TransformRule


def _by_name(fields: list[FieldSchema]) -> dict[str, FieldSchema]:
    return {field.field_name: field for field in fields}


def _default_for_type(field_type: str):
    if field_type in {"number", "int", "integer", "float", "decimal"}:
        return 0
    if field_type in {"bool", "boolean"}:
        return False
    return ""


def infer_rule_type(source: FieldSchema | None, target: FieldSchema) -> RuleType:
    if source is None:
        return RuleType.DEFAULT_VALUE
    if "date" in source.type and "date" in target.type:
        return RuleType.DATE_FORMAT
    if source.example and target.example and str(source.example).lower() != str(target.example).lower():
        if source.type in {"string", "str", "text"} and target.type in {"string", "str", "text"}:
            return RuleType.ENUM_MAPPING
    return RuleType.DIRECT


def generate_rules(
    mappings: list[FieldMapping],
    source_fields: list[FieldSchema],
    target_fields: list[FieldSchema],
    include_review: bool = True,
) -> list[TransformRule]:
    """Create simple executable transform rules from confirmed and reviewable mappings."""
    sources = _by_name(source_fields)
    targets = _by_name(target_fields)
    rules: list[TransformRule] = []

    for mapping in mappings:
        target = targets[mapping.target_field]
        source = sources.get(mapping.source_field or "")
        if mapping.status == MappingStatus.UNMATCHED:
            if target.required:
                rules.append(
                    TransformRule(
                        target_field=target.field_name,
                        rule_type=RuleType.DEFAULT_VALUE,
                        default_value=_default_for_type(target.type),
                    )
                )
            continue
        if mapping.status == MappingStatus.NEED_REVIEW and not include_review:
            continue

        rule_type = infer_rule_type(source, target)
        mapping.rule_type = rule_type
        rules.append(
            TransformRule(
                source_field=source.field_name if source else None,
                target_field=target.field_name,
                rule_type=rule_type,
                default_value=_default_for_type(target.type) if rule_type == RuleType.DEFAULT_VALUE else None,
                enum_map={str(source.example): target.example} if source and rule_type == RuleType.ENUM_MAPPING else {},
                date_input_format="%Y-%m-%d",
                date_output_format="%Y-%m-%d",
            )
        )
    return rules
