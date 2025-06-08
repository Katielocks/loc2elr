from __future__ import annotations
import gzip
import json
import logging
import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Callable, Union

import pandas as pd
import numpy as np
from pyproj import Transformer

log = logging.getLogger(__name__)

class ELRClientError(Exception):
    pass

class ZipFileNotFoundError(ELRClientError):
    pass

def _open_zip(input_path: Union[str, Path]) -> Path:
    zip_path = Path(input_path).expanduser().resolve()
    if not zip_path.exists():
        raise FileNotFoundError(f"Local Track Model not found at {zip_path}")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            members = zf.namelist()
            stem = "nwr_trackcentrelines"
            required = {ext: None for ext in (".shp", ".shx", ".dbf")}
            for m in members:
                p = Path(m)
                if p.stem.lower() == stem and p.suffix.lower() in required:
                    required[p.suffix.lower()] = m

            if not all(required.values()):
                missing = [ext for ext, path in required.items() if path is None]
                raise ELRClientError(
                    f"Missing {', '.join(missing)} for {stem} in {zip_path.name}"
                )

            temp_dir = Path(tempfile.mkdtemp(prefix="NWR_TM_"))
            for member in required.values():
                zf.extract(member, path=temp_dir)

            return temp_dir / f"{stem}.shp"

    except zipfile.BadZipFile as exc:
        raise ELRClientError(f"Invalid ZIP at {zip_path}: {exc}") from exc
    except ELRClientError:
        raise
    except Exception as exc:
        raise ELRClientError(f"Error processing {zip_path}: {exc}") from exc


def get_elr(input_path: Union[str, Path]) -> Path:
    input_path = Path(input_path).expanduser().resolve()

    if input_path.suffix.lower() == ".zip":
        shp = _open_zip(input_path)

    elif input_path.suffix.lower() == ".shp" and input_path.is_file():
        stem = input_path.stem
        parent = input_path.parent
        for ext in [".shx", ".dbf"]:
            sibling = parent / f"{stem}{ext}"
            if not sibling.exists():
                raise ELRClientError(
                    f"Missing {ext} for {stem} in {parent}"
                )
        shp = input_path

    elif input_path.is_dir():
        stem = "nwr_trackcentrelines"
        for ext in [".shp", ".shx", ".dbf"]:
            p = input_path / f"{stem}{ext}"
            if not p.exists():
                raise ELRClientError(
                    f"Missing {ext} for {stem} in {input_path}"
                )
        shp = input_path / f"{stem}.shp"

    else:
        raise FileNotFoundError(f"ELR source not found at {input_path}")

    return shp
