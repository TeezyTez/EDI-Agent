from pathlib import Path

from app.config import GENERATED_DIR, REPORT_DIR, TEST_DIR, ensure_workspace
from app.models.schema import AgentResult
from app.services.code_generator import generate_transform_code
from app.services.document_parser import parse_field_schema
from app.services.field_matcher import generate_mapping_table
from app.services.report_generator import generate_report
from app.services.rule_generator import generate_rules
from app.services.test_generator import generate_pytest_file
from app.services.test_runner import run_pytest


def run_mapping_workflow(
    source_fields_path: str | Path,
    target_fields_path: str | Path,
    source_sample_path: str | Path,
    target_sample_path: str | Path,
) -> AgentResult:
    """Execute the local rule-based EDI mapping workflow end to end."""
    ensure_workspace()
    source_fields = parse_field_schema(source_fields_path)
    target_fields = parse_field_schema(target_fields_path)
    mappings = generate_mapping_table(source_fields, target_fields)
    rules = generate_rules(mappings, source_fields, target_fields)
    transform_path = generate_transform_code(rules, GENERATED_DIR)
    test_path = generate_pytest_file(source_sample_path, target_sample_path, TEST_DIR)
    pytest_passed, pytest_output = run_pytest(TEST_DIR)
    report_path = generate_report(mappings, transform_path, test_path, pytest_passed, pytest_output, REPORT_DIR)
    return AgentResult(
        mappings=mappings,
        rules=rules,
        transform_path=str(transform_path),
        test_path=str(test_path),
        report_path=str(report_path),
        pytest_passed=pytest_passed,
        pytest_output=pytest_output,
    )
