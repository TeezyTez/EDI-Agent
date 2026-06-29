import sys
from pathlib import Path


GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
sys.path.insert(0, str(GENERATED_DIR))

from transform import transform_record


SOURCE_RECORD = {'order_id': 'SO-1001', 'customer_name': 'Acme Trading', 'order_date': '2026-06-22', 'amount': 199.5, 'currency': 'USD', 'status': 'NEW'}
TARGET_RECORD = {'order_id': 'SO-1001', 'buyer_name': 'Acme Trading', 'order_date': '2026-06-22', 'total_amount': 199.5, 'currency_code': 'USD', 'order_status': 'Created'}


def test_transform_contains_expected_target_fields():
    result = transform_record(SOURCE_RECORD)
    assert set(TARGET_RECORD).issubset(set(result))


def test_transform_matches_sample_values_for_generated_fields():
    result = transform_record(SOURCE_RECORD)
    for key, expected in TARGET_RECORD.items():
        assert result.get(key) == expected
