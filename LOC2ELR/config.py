from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = ["settings", "IOCfg", "ModelCfg", "OutputCfg", "Settings"]


@dataclass(frozen=True, slots=True)
class IOCfg:
    bplan: Path
    track_model: Path


@dataclass(frozen=True, slots=True)
class ModelCfg:
    loc_id_field: str
    elr_id_field: str
    start_id_field: str
    max_distance_m: float
    seg_length_mi: int


@dataclass(frozen=True, slots=True)
class OutputCfg:
    output: Path


@dataclass(frozen=True, slots=True)
class Settings:
    io: IOCfg
    model: ModelCfg
    output: OutputCfg



def _to_path(p: str | Path) -> Path:
    return p if isinstance(p, Path) else Path(p)



def _load_settings() -> Settings:

    settings_path = Path(__file__).with_name("settings.json")
    if not settings_path.is_file():
        raise FileNotFoundError(
            f"Expected a settings.json next to {__file__!s}, "
            f"but could not find one at {settings_path!s}"
        )

    raw: dict[str, Any] = json.loads(settings_path.read_text())

    try:
        io_cfg = IOCfg(
            bplan=_to_path(raw["io"]["BPLAN"]),
            track_model=_to_path(raw["io"]["TRACK_MODEL"]),
        )

        model_cfg = ModelCfg(
            loc_id_field=str(raw["model"]["LOC_ID_FIELD"]),
            elr_id_field=str(raw["model"]["ELR_ID_FIELD"]),
            start_id_field=str(raw["model"]["START_ID_FIELD"]),
            max_distance_m=float(raw["model"]["MAX_DISTANCE_M"]),
            seg_length_mi=int(raw["model"]["SEG_LENGTH_MI"])
        )
        output_cfg = OutputCfg(
            output=_to_path(raw["output"]["OUTPUT_DIR"]),
        )
    except KeyError as exc:
        missing = " ➜ ".join(str(p) for p in exc.args)
        raise KeyError(f"Missing expected key in settings.json: {missing}") from exc

    return Settings(io=io_cfg, model=model_cfg, output=output_cfg)


settings: Settings = _load_settings()
