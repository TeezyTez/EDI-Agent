from app.models.schema import FieldSchema, MappingStatus
from app.services.field_matcher import generate_mapping_table


def test_generate_mapping_table_matches_similar_fields():
    sources = [
        FieldSchema(field_name="order_id", description="Order identifier", type="string", required=True, example="SO-1001"),
        FieldSchema(field_name="amount", description="Total amount", type="number", required=True, example=199.5),
    ]
    targets = [
        FieldSchema(field_name="order_id", description="Order identifier", type="string", required=True, example="SO-1001"),
        FieldSchema(field_name="total_amount", description="Total amount", type="number", required=True, example=199.5),
    ]

    mappings = generate_mapping_table(sources, targets)

    assert mappings[0].status == MappingStatus.AUTO_CONFIRMED
    assert mappings[0].source_field == "order_id"
    assert mappings[1].source_field == "amount"
