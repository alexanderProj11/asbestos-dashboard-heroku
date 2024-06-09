import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def find_cfsauid(lat, lon, polygons_gdf):
    """
    Finds the CFSAUID for a given latitude and longitude by checking which polygon the point falls into.

    Parameters:
    lat (float): Latitude of the point.
    lon (float): Longitude of the point.
    polygons_gdf (GeoDataFrame): GeoDataFrame containing the polygons and their CFSAUIDs.

    Returns:
    str: The CFSAUID of the polygon containing the point, or None if no polygon contains the point.
    """
    point = Point(lon, lat)
    for _, row in polygons_gdf.iterrows():
        if row['geometry'].contains(point):
            return row['CFSAUID']
    return None

def add_forward_sortation_area(input_csv, geojson_file, output_csv):
    """
    Reads a CSV file with latitude and longitude columns, finds the corresponding CFSAUID for each point,
    and writes the result to a new column "Forward_Sortation_Area".

    Parameters:
    input_csv (str): Path to the input CSV file.
    geojson_file (str): Path to the GeoJSON file containing the polygons.
    output_csv (str): Path to the output CSV file where results will be saved.
    """
    # Read the input CSV file
    df = pd.read_csv(input_csv)

    # Read the GeoJSON file
    polygons_gdf = gpd.read_file(geojson_file)

    # Ensure the GeoDataFrame has the necessary column
    if 'CFSAUID' not in polygons_gdf.columns:
        raise ValueError("GeoJSON file must contain 'CFSAUID' column.")

    # Find the CFSAUID for each point and create a new column
    df['Forward_Sortation_Area'] = df.apply(
        lambda row: find_cfsauid(row['Latitude'], row['Longitude'], polygons_gdf), axis=1
    )

    # Save the updated DataFrame to the output CSV file
    df.to_csv(output_csv, index=False)
    print(f"Output saved to {output_csv}")

# Example usage
input_csv = 'AsbestosDataCSV.csv'
geojson_file = 'output_geojson_manitoba_fsa.geojson'
output_csv = 'output_asbestos_fsa.csv'

add_forward_sortation_area(input_csv, geojson_file, output_csv)
