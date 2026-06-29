from pathlib import Path
from typing import Any

from app.utils.json_utils import load_json


def _first_record(data: Any) -> dict:
    if isinstance(data, list):
        return data[0] if data else {}
    if isinstance(data, dict):
        return data
    return {}


def generate_pytest_file(source_sample_path: str | Path, target_sample_path: str | Path, test_dir: str | Path) -> Path:
    """Generate pytest checks that compare generated transform output to sample target data."""
    source_record = _first_record(load_json(source_sample_path))
    target_record = _first_record(load_json(target_sample_path))
    target = Path(test_dir)
    target.mkdir(parents=True, exist_ok=True)
    output_path = target / "test_transform.py"
    output_path.write_text(
        f'''import sys
from pathlib import Path


GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
sys.path.insert(0, str(GENERATED_DIR))

from transform import transform_record


SOURCE_RECORD = {source_record!r}
TARGET_RECORD = {target_record!r}


def test_transform_contains_expected_target_fields():
    result = transform_record(SOURCE_RECORD)
    assert set(TARGET_RECORD).issubset(set(result))


def test_transform_matches_sample_values_for_generated_fields():
    result = transform_record(SOURCE_RECORD)
    for key, expected in TARGET_RECORD.items():
        assert result.get(key) == expected
''',
        encoding="utf-8",
    )
    return output_path
