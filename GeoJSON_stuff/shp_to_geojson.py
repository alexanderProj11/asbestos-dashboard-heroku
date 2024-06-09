import geopandas as gpd
import pyproj
from shapely.ops import transform
import json

# Function to reproject geometry
def reproject_geometry(geometry, src_crs, dest_crs):
    project = pyproj.Transformer.from_crs(src_crs, dest_crs, always_xy=True).transform
    return transform(project, geometry)

# File paths
input_shapefile = 'Shapefile/lfsa000a16a_e.shp'
output_geojson = 'output_geojson_allcanada_fsa.geojson'

# Read the shapefile
gdf = gpd.read_file(input_shapefile)

# Define the source and destination CRS
src_crs = 'epsg:3347'  # The EPSG code for PCS_Lambert_Conformal_Conic (you may need to verify this)
dest_crs = 'epsg:4326'  # The EPSG code for WGS 84

# Reproject the GeoDataFrame
gdf = gdf.to_crs(dest_crs)

# Filter the GeoDataFrame for specific province
gdf_filtered = gdf[gdf['PRNAME'] == 'Manitoba']

# Save to GeoJSON - uncomment if filtering for specific province
gdf_filtered.to_file(output_geojson, driver='GeoJSON')

# gdf.to_file(output_geojson, driver='GeoJSON')

print(f"GeoJSON file has been saved to {output_geojson}")
