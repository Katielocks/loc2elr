from __future__ import annotations

import gzip
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import numpy as np
from pyproj import Transformer



log = logging.getLogger(__name__)

_TRANSFORMER = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

_FIELDS = [
    "RECORD_TYPE",
    "ACTION_CODE",
    "TIPLOC",
    "LOC_NAME",
    "START_DATE",
    "END_DATE",
    "OS_EASTING",
    "OS_NORTHING",
    "TIMING_POINT_TYPE",
    "ZONE",
    "STANOX",
    "OFF_NETWORK",
    "LPB",
]


class BplanClientError(RuntimeError):
    """Raised whenever we can't fetch/unpack/parse the BPLAN doc."""


def _parse_loc_records(file_path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    open_func = gzip.open if file_path.suffix == ".gz" else open
    mode = "rt" if file_path.suffix == ".gz" else "r"

    with open_func(file_path, mode=mode, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            if not raw.startswith("LOC"):
                continue

            parts = raw.rstrip("\n").split("\t")
            row = {k: v for k, v in zip(_FIELDS, parts)}
            records.append(row)

    return records



def get_bplan(input_path:str | Path):

    try:
        zip_path = Path(input_path).expanduser().resolve()
        if not zip_path.exists():
            raise FileNotFoundError(f"Local BPLAN not found at {zip_path}")
    except Exception as exc:
        raise BplanClientError(f"Could not locate BPLAN: {exc}") from exc

    try:
        with zipfile.ZipFile(zip_path) as zf:
            members = zf.namelist()
            candidate = None
            for m in members:
                lower = m.lower()
                if lower.endswith(".txt.gz") or lower.endswith(".txt"):
                    candidate = m
                    break
            if candidate is None:
                raise BplanClientError(
                    f"No .txt or .txt.gz found inside {zip_path.name}"
                )

            with tempfile.TemporaryDirectory() as td:
                extracted = zf.extract(candidate, path=td)
                loc_records = _parse_loc_records(Path(extracted))
    except Exception as exc:
        raise BplanClientError(f"Failed to unpack/parse BPLAN: {exc}") from exc

    try:
        df = pd.DataFrame(loc_records)
        df["OS_EASTING"] = pd.to_numeric(df["OS_EASTING"], errors="coerce")
        df["OS_NORTHING"] = pd.to_numeric(df["OS_NORTHING"], errors="coerce")
        df["STANOX"] = df["STANOX"].replace(r"^\s*$", np.nan, regex=True)

        df = df[df["STANOX"].notna()]
        df = df[df["OS_EASTING"].notna() & df["OS_EASTING"].ne(0) & df["OS_EASTING"].ne(999_999)] #Removing Placeholder values
    except Exception as exc:
        raise BplanClientError(f"Error processing BPLAN DataFrame: {exc}") from exc

    return df
