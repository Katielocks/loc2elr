from pathlib import Path
import importlib.util

REPO_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "loc2elr.config", REPO_ROOT / "loc2elr" / "config.py"
)
config = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = config
spec.loader.exec_module(config)
_to_path = config._to_path

def test_to_path_with_str():
    p = _to_path('foo/bar')
    assert isinstance(p, Path)
    assert p == Path('foo/bar')

def test_to_path_with_path_obj():
    p = Path('bar/baz')
    assert _to_path(p) is p