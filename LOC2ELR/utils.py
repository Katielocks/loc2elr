from __future__ import annotations
from typing import Callable
import pandas as pd


INPUT_METHOD: dict[str, Callable] = {
    "csv":    pd.read_csv,
    "parquet":pd.read_parquet,
    "json":   pd.read_json,
    "excel":  pd.read_excel
}


OUTPUT_METHOD: dict[str, Callable] = {
    "csv":    pd.DataFrame.to_csv,
    "parquet":pd.DataFrame.to_parquet,
    "json":   pd.DataFrame.to_json,
    "excel":  pd.DataFrame.to_excel
}
