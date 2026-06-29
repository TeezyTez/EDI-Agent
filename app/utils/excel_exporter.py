from pathlib import Path

import pandas as pd

from app.models.schema import FieldMapping


def export_mappings_to_excel(mappings: list[FieldMapping], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([mapping.model_dump() for mapping in mappings]).to_excel(target, index=False)
    return target
