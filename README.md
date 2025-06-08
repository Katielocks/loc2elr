# loc2elr

**loc2elr** is a Python library for mapping UK rail STANOX location codes into contiguous ELR mile markers (e.g., `SWM2_112`). It provides modular, granular spatial data analysis buckets.

## Required Data

- **BPLAN**  
  ZIP archives containing BPLAN shapefiles and `.loc` records.  
  Sources:  
  - [Rail Data UK](https://www.raildata.org.uk/)  
  - [OpenRailData Archive](https://github.com/raildata/openraildata)

- **NWR Track Model**  
  ESRI shapefiles for the Network Rail Track Model (e.g. `NWR_TrackCentreLines.shp`).  
  Source: [Rail Data UK](https://www.raildata.org.uk/)

## Features

- **BPLAN parser**  
  Reads and extracts station and location records from BPLAN ZIP archives.

- **Track importer**  
  Loads shapefiles, directories or ZIP archives of NWR Track Model data using a context-managed temporary file to avoid resource leaks.

- **`loc2elr`**  
  High-level function that ties together BPLAN and NWR Track Model I/O, mapping STANOX codes to ELR mile-bucket identifiers.  
  - Pass `seg_length=None` or `0` to return only the raw ELR ID (without bucketing).

- **`link_bplan_to_elr`**  
  Lower-level function to join a GeoDataFrame of points (BPLAN) with track segments (ELR), compute distances, bucket by segment length, and generate the `ELR_MIL` column.

- **Configurable defaults**  
  All thresholds, column names, CRS and I/O paths can be overridden via `settings.json` or directly as function parameters.

## Installation

```bash
pip install git+https://github.com/katielocks/loc2elr.git

```
`loc2elr`
```python 
from loc2elr import loc2elr

# End-to-end processing: BPLAN → NWR Track Model to CSV output
result_df = loc2elr(
    bplan_source="data/BPLAN.zip",
    track_source="data/NWR_Track_Model.zip",
    output_path="output/stnox_buckets.csv",
)

print(result_df.head())
```
`link_bplan_to_elr`
```python 
from loc2elr import link_bplan_to_elr
import geopandas as gpd

# Load your geospatial data
track_gdf = gpd.read_file("data/NWR_TrackModel/NWR_TrackCentreLines.shp")

# Compute ELR mile buckets without writing to disk
buckets_df = link_bplan_to_elr(
    bplan_gdf=bplan_gdf,
    track_gdf=track_gdf,
    max_distance_m=1000,  # maximum join distance in metres
    seg_length=5,         # bucket interval in miles
)

print(buckets_df["ELR_MIL"].unique())
```



   ```bash
   pip install git+https://github.com/katielocks/loc2elr.git
   ```
