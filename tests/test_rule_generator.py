from app.models.schema import FieldMapping, FieldSchema, MappingStatus, RuleType
from app.services.rule_generator import generate_rules


def test_generate_rules_adds_default_for_required_unmatched_target():
    target = FieldSchema(field_name="currency", description="Currency", type="string", required=True, example="USD")
    mappings = [
        FieldMapping(
            source_field=None,
            target_field="currency",
            confidence=0,
            reason="No match",
            status=MappingStatus.UNMATCHED,
        )
    ]

    rules = generate_rules(mappings, [], [target])

    assert rules[0].rule_type == RuleType.DEFAULT_VALUE
    assert rules[0].target_field == "currency"
