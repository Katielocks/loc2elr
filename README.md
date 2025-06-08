# loc2elr

loc2elr is a Python library for mapping UK rail STANOX location codes into contiguous ELR mile markers (e.g., SWM2_112). It provides modular granularity spatial data analysis buckets.
```python 
from loc2elr import loc2elr

# Run end-to-end processing from BPLAN & NWR Track Model to output file
result_df = loc2elr(
    bplan_source="data/BPLAN_geography.shp",
    track_source="data/NWR_Track_Model.csv",
    output_path="output/stnox_buckets.csv",
)

# Inspect the resulting DataFrame
print(result_df.head())
```
```python 
import geopandas as gpd

# Load your geospatial data
bplan_gdf = gpd.read_file("data/BPLAN_geography.shp")
track_gdf = gpd.read_file("data/NWR_Track_Model.csv")

# Compute buckets without writing to disk
buckets_df = link_bplan_to_elr(
    bplan_gdf=bplan_gdf,
    track_gdf=track_gdf,
    max_distance_m=1000,        # override defaults if needed
    seg_length=5,
)

# Examine results
print(buckets_df["ELR_MIL"].unique())
```



   ```bash
   pip install git+https://github.com/katielocks/loc2elr.git
   ```