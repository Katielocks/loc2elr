import zipfile
from pathlib import Path
import sys
import importlib.util

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "loc2elr.track_client", REPO_ROOT / "loc2elr" / "track_client.py"
)
track_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(track_client)

_open_zip = track_client._open_zip
_validate_standalone_shp = track_client._validate_standalone_shp
ELRClientError = track_client.ELRClientError
ZipFileNotFoundError = track_client.ZipFileNotFoundError


def _create_dummy_shp(dir_path: Path):
    stem = "nwr_trackcentrelines"
    shp = dir_path / f"{stem}.shp"
    shx = dir_path / f"{stem}.shx"
    dbf = dir_path / f"{stem}.dbf"
    for p in (shp, shx, dbf):
        p.write_text("dummy")
    return shp, shx, dbf


def test_validate_standalone_shp(tmp_path: Path):
    shp, shx, dbf = _create_dummy_shp(tmp_path)
    result = _validate_standalone_shp(shp)
    assert result == shp


def test_open_zip_extracts(tmp_path: Path):
    shp, shx, dbf = _create_dummy_shp(tmp_path)
    zip_path = tmp_path / "track.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for p in (shp, shx, dbf):
            zf.write(p, p.name)
    for p in (shp, shx, dbf):
        p.unlink()
    with _open_zip(zip_path) as extracted:
        assert extracted.is_file()
        assert extracted.name == "nwr_trackcentrelines.shp"
    assert not extracted.exists()


def test_open_zip_missing(tmp_path: Path):
    with pytest.raises(ZipFileNotFoundError):
        with _open_zip(tmp_path / "missing.zip"):
            pass


def test_validate_missing_parts(tmp_path: Path):
    shp = tmp_path / "nwr_trackcentrelines.shp"
    shp.write_text("dummy")
    with pytest.raises(ELRClientError):
        _validate_standalone_shp(shp)