from __future__ import annotations

import os
from pathlib import Path
from typing import Union, Optional

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from bplan_client import get_bplan
from ELR_client import get_elr
from utils import OUTPUT_METHOD
from config import settings as cfg



class   LOC2ELR(RuntimeError):
    """Raised whenever we can't fetch/unpack/parse the BPLAN doc."""


def Loc2ELRMiles(
    bplan_source: Union[str, Path] = cfg.io.bplan,
    track_source: Union[str, Path] = cfg.io.track_model,
    *,
    output_path: Optional[Union[str, Path]] = cfg.output.output,
    max_distance:  float  = cfg.model.max_distance_m,
    seg_length:    int    = cfg.model.seg_length_mi,
    loc_col:       str    = cfg.model.loc_id_field,
    elr_col:       str    = cfg.model.elr_id_field,
    start_col:     str    = cfg.model.start_id_field,  
    easting_col:   str    = "OS_EASTING",
    northing_col:  str    = "OS_NORTHING",
) -> pd.DataFrame:

    bplan_df = get_bplan(bplan_source)

    required_cols = {loc_col, easting_col, northing_col}
    missing = required_cols - set(bplan_df.columns)
    if missing:
        raise ValueError(f"BPlan missing required columns: {sorted(missing)}")

    track_path = get_elr(track_source)     
    track_gdf = gpd.read_file(track_path)

    osgb_crs = "EPSG:27700"
    if track_gdf.crs is None:
        track_gdf.set_crs(osgb_crs, inplace=True)
    track_gdf = track_gdf.to_crs(osgb_crs)

    if not isinstance(bplan_df, gpd.GeoDataFrame):
        bplan_gdf = gpd.GeoDataFrame(
            bplan_df,
            geometry=gpd.points_from_xy(bplan_df[easting_col],
                                        bplan_df[northing_col]),
            crs=osgb_crs,
        )
    else:
        bplan_gdf = bplan_df.to_crs(osgb_crs)
        track_path = get_elr(track_source)        
    track_gdf   = gpd.read_file(track_path)

    track_gdf = track_gdf[[elr_col, start_col, "geometry"]]

    track_gdf = track_gdf.set_crs("EPSG:27700", allow_override=True).to_crs("EPSG:27700")

    # -------------------------------------------------------------------
    nearest = gpd.sjoin_nearest(
        bplan_gdf,
        track_gdf,
        how="left",
        max_distance=max_distance,
        distance_col=f"{start_col}_DIST",
    )
    # -------------------------------------------------------------------
    out_df = nearest[[loc_col, elr_col, easting_col, northing_col, start_col]]
    if seg_length:
        out_df[start_col] = (
        out_df[start_col]
        .fillna(0)
        .astype(int)
        .floordiv(seg_length)  
        .mul(seg_length)      
        )
    out_df["ELR_MIL"] = out_df[elr_col] + "_" + out_df[start_col].astype("str") 
    out_df = out_df.drop(columns=[elr_col,start_col])
    if output_path:
        out_path = Path(output_path).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        output_format = out_path.suffix.lstrip(".")
        try:
            OUTPUT_METHOD[output_format.lower()](out_df, out_path,index=False)
        except KeyError as exc:
            raise (str(exc))
        except Exception as exc:
            raise  LOC2ELR(
                f"Could not write {output_format.upper()} to {out_path}: {exc}"
            ) from exc

Loc2ELRMiles()