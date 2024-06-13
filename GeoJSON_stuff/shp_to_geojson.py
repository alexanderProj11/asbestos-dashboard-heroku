import geopandas as gpd
import pyproj
from shapely.ops import transform
import json

# Function to reproject geometry
def reproject_geometry(geometry, src_crs, dest_crs):
    project = pyproj.Transformer.from_crs(src_crs, dest_crs, always_xy=True).transform
    return transform(project, geometry)

# File paths
input_shapefile = '/workspaces/asbestos-dashboard-heroku/GeoJSON_stuff/Shapefile/electoral_districs_can/lfed000b21a_e.shp'
output_geojson = 'fed_electoral_output_geojson_manitoba.geojson'

# Read the shapefile
gdf = gpd.read_file(input_shapefile)

# Define the source and destination CRS
src_crs = 'epsg:3347'  # The EPSG code for PCS_Lambert_Conformal_Conic (you may need to verify this)
dest_crs = 'epsg:4326'  # The EPSG code for WGS 84

# Reproject the GeoDataFrame
gdf = gdf.to_crs(dest_crs)

# Filter the GeoDataFrame for specific province
# gdf_filtered = gdf[gdf['PRNAME'] == 'Manitoba']
gdf_filtered = gdf[gdf['PRUID'] == "46"]

# Save to GeoJSON - uncomment if filtering for specific province
gdf_filtered.to_file(output_geojson, driver='GeoJSON')

# gdf.to_file(output_geojson, driver='GeoJSON')

print(f"GeoJSON file has been saved to {output_geojson}")
