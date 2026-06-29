from pathlib import Path

from app.models.schema import FieldMapping, MappingStatus


def _markdown_table(mappings: list[FieldMapping]) -> str:
    lines = [
        "| source_field | target_field | confidence | rule_type | status | reason |",
        "|---|---|---:|---|---|---|",
    ]
    for item in mappings:
        lines.append(
            f"| {item.source_field or ''} | {item.target_field} | {item.confidence:.2f} | "
            f"{item.rule_type.value} | {item.status.value} | {item.reason} |"
        )
    return "\n".join(lines)


def generate_report(
    mappings: list[FieldMapping],
    transform_path: str | Path,
    test_path: str | Path,
    pytest_passed: bool,
    pytest_output: str,
    report_dir: str | Path,
) -> Path:
    target = Path(report_dir)
    target.mkdir(parents=True, exist_ok=True)
    output_path = target / "report.md"
    unmatched = [item for item in mappings if item.status == MappingStatus.UNMATCHED]
    review = [item for item in mappings if item.status == MappingStatus.NEED_REVIEW]
    report = f"""# EDI Mapping Agent Report

## Field Mapping Table

{_markdown_table(mappings)}

## Unmatched Fields

{_markdown_table(unmatched) if unmatched else "No unmatched fields."}

## Need Human Review

{_markdown_table(review) if review else "No fields need review."}

## Generated Artifacts

- Transform code: `{Path(transform_path).as_posix()}`
- Pytest file: `{Path(test_path).as_posix()}`

## Test Result

- Passed: `{pytest_passed}`

```text
{pytest_output.strip()}
```
"""
    output_path.write_text(report, encoding="utf-8")
    return output_path
