import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the CSV file
csv_file = 'all_Valid_Addresses_3.csv'
df = pd.read_csv(csv_file)

# Load the GeoJSON file
geojson_file = 'output_geojson_manitoba_fsa.geojson'
gdf = gpd.read_file(geojson_file)

# Create a GeoDataFrame from the CSV data
geometry = [Point(float(lon), float(lat)) for lon, lat in zip(df['Longitude'], df['Latitude'])]
df_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Spatial join to find the correct Forward Sortation Area
df_gdf = gpd.sjoin(df_gdf, gdf[['geometry', 'CFSAUID']], how='left', op='within')

# Compare the original and new Forward Sortation Area
df_gdf['FSA_Match'] = df_gdf['Forward_Sortation_Area'] == df_gdf['CFSAUID']

# Separate the rows with mismatched FSAs
errors_df = df_gdf[~df_gdf['FSA_Match']].copy()

# Prepare the error DataFrame for saving
errors_df = errors_df[['confirmationNo', 'Latitude', 'Longitude', 'formattedAddress', 'Forward_Sortation_Area', 'CFSAUID']]
errors_df.columns = ['confirmationNo', 'Latitude', 'Longitude', 'Original FSA', 'New FSA']

# Save the errors to a new CSV file
errors_df.to_csv('fsa_manitoba_errors.csv', index=False)

# Remove the rows with mismatched FSAs from the original DataFrame
df_gdf = df_gdf[df_gdf['FSA_Match']]

# Drop the extra columns and save the cleaned DataFrame back to CSV
df_gdf = df_gdf.drop(columns=['geometry', 'index_right', 'FSA_Match'])
df_gdf.to_csv(csv_file, index=False)