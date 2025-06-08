from __future__ import annotations

import sys
import json
import logging
from pathlib import Path
from typing import Callable, Optional

import geopandas as gpd
import pandas as pd

from .bplan_client import get_bplan
from .ELR_client import get_elr
from .config import settings as cfg

__all__ = [
    "link_bplan_to_elr",
    "loc2elr"
]

log = logging.getLogger(__name__)


def link_bplan_to_elr(
    bplan_gdf: gpd.GeoDataFrame,
    track_gdf: gpd.GeoDataFrame,
    *,
    loc_col: str = cfg.model.loc_id,
    easting_col: str = "EASTING",
    northing_col: str = "NORTHING",
    elr_col: str = cfg.model.elr_id,
    start_col: str = cfg.model.start_id,
    max_distance_m: float = cfg.model.max_distance_m,
    seg_length: int = cfg.model.seg_length_mi
) -> pd.DataFrame:

    bplan = bplan_gdf.copy()
    track = track_gdf.copy()

    osgb = "EPSG:27700"
    if bplan.crs != osgb:
        raise ValueError("bplan_gdf CRS must be EPSG:27700")
    if track.crs != osgb:
        raise ValueError("track_gdf CRS must be EPSG:27700")

    missing_bplan = {loc_col, easting_col, northing_col} - set(bplan.columns)
    if missing_bplan:
        raise KeyError(f"BPlan missing columns: {sorted(missing_bplan)}")

    missing_track = {elr_col, start_col} - set(track.columns)
    if missing_track:
        raise KeyError(f"Track model missing columns: {sorted(missing_track)}")


    if not isinstance(bplan, gpd.GeoDataFrame):
        bplan = gpd.GeoDataFrame(
            bplan,
            geometry=gpd.points_from_xy(bplan[easting_col], bplan[northing_col]),
            crs=osgb,
        )

    track = track[[elr_col, start_col, "geometry"]]

    joined = gpd.sjoin_nearest(
        bplan,
        track,
        how="left",
        max_distance=max_distance_m,
        distance_col="DIST_M",
    )

    out_df = pd.DataFrame(joined.drop(columns=["geometry", "index_right"]))
    if seg_length:
        out_df[start_col] = (
        out_df[start_col]
        .fillna(0)
        .astype(int)
        .floordiv(seg_length)  
        .mul(seg_length)      
        )
    out_df["ELR_MIL"] = (
        out_df[elr_col].fillna("UNKNOWN") + "_" + out_df[start_col].astype("str")
    )
    return out_df


_OUTPUT_WRITERS: dict[str, Callable[[pd.DataFrame, Path], None]] = {
    "csv": lambda df, p: df.to_csv(p, index=False),
    "parquet": lambda df, p: df.to_parquet(p, index=False),
    "json": lambda df, p: df.to_json(p, orient="records"),
}


def loc2elr(
    *,
    bplan_source: str | Path | None = None,
    track_source: str | Path | None = None,
    output_path: str | Path | None = None,
    loc_col: str = cfg.model.loc_id,
    easting_col: str = "EASTING",
    northing_col: str = "NORTHING",
    elr_col: str = cfg.model.elr_id,
    start_col: str = cfg.model.start_id,
    max_distance_m: float = cfg.model.max_distance_m,
    seg_length_mi: int = cfg.model.seg_length_mi
) -> pd.DataFrame:

    bplan_source = bplan_source or cfg.io.bplan
    track_source = track_source or cfg.io.track_model
                                                                   
    bplan_gdf = (
        get_bplan(bplan_source) if not isinstance(bplan_source, gpd.GeoDataFrame) else bplan_source
    )

    with get_elr(track_source) as track_path:
        track_gdf = gpd.read_file(track_path)
        if track_gdf.crs is None:
            track_gdf.set_crs("EPSG:27700", inplace=True)

    out_df = link_bplan_to_elr(
        bplan_gdf=bplan_gdf,
        track_gdf=track_gdf,
        loc_col=loc_col,
        easting_col=easting_col,
        northing_col=northing_col,
        elr_col=elr_col,
        start_col=start_col,
        max_distance_m=max_distance_m,
        seg_length_mi=seg_length_mi
    )
                                                        
    if output_path is not None:
        out_path = Path(output_path).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = out_path.suffix.lstrip(".").lower()
        try:
            _OUTPUT_WRITERS[fmt](out_df, out_path)
        except KeyError:
            raise ValueError(
                f"Unsupported output format ‘{fmt}’. Choose one of {list(_OUTPUT_WRITERS)}"
            ) from None
        log.info("Wrote %s records ➜ %s", len(out_df), out_path)

    return out_df