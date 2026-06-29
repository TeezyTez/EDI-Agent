from pathlib import Path
from typing import Any

import pandas as pd

from app.models.schema import FieldSchema


REQUIRED_COLUMNS = {"field_name", "description", "type", "required", "example"}


def _read_table(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(source)
    raise ValueError(f"Unsupported field document format: {source.suffix}")


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "required", "是", "√"}


def parse_field_schema(path: str | Path) -> list[FieldSchema]:
    """Parse CSV or Excel field documentation into normalized FieldSchema objects."""
    df = _read_table(path)
    df.columns = [str(column).strip() for column in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Field document is missing columns: {', '.join(sorted(missing))}")

    fields: list[FieldSchema] = []
    for _, row in df.iterrows():
        fields.append(
            FieldSchema(
                field_name=str(row["field_name"]).strip(),
                description="" if pd.isna(row["description"]) else str(row["description"]).strip(),
                type="string" if pd.isna(row["type"]) else str(row["type"]).strip().lower(),
                required=_to_bool(row["required"]),
                example=None if pd.isna(row["example"]) else row["example"],
            )
        )
    return fields
