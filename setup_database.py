import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging
from config import get_database_url, get_csv_file_path_1, get_csv_file_path_2
from scipy.spatial import cKDTree
import numpy as np

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_density_column(df):
    """
    Calculate the density column based on the distribution of data points.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing latitude and longitude columns.
    
    Returns:
    pd.Series: The calculated density column.
    """
    try:
        # Reset DataFrame index to ensure alignment
        df.reset_index(drop=True, inplace=True)
        
        # Debug: Print shape of DataFrame
        logging.info(f"DataFrame shape: {df.shape}")
        
        # Check for empty DataFrame
        if df.empty:
            logging.error("DataFrame is empty.")
            return pd.Series()

        # Define grid size or bins
        grid_size = 0.01  # Define grid cell size (adjust as needed)

        # Calculate the number of grid cells in latitude and longitude directions
        lat_bins = np.linspace(df['Latitude'].min(), df['Latitude'].max(), num=8090)
        lon_bins = np.linspace(df['Longitude'].min(), df['Longitude'].max(), num=10530)

        # Debug: Print dimensions of lat_bins and lon_bins
        logging.info(f"lat_bins dimensions: {lat_bins.shape}")
        logging.info(f"lon_bins dimensions: {lon_bins.shape}")

        # Create a 2D histogram to count the number of data points in each grid cell
        hist, _, _ = np.histogram2d(df['Latitude'], df['Longitude'], bins=[lat_bins, lon_bins])
        
        # Debug: Print dimensions of hist
        logging.info(f"hist dimensions: {hist.shape}")

        # Create a KDTree for efficient nearest neighbor search
        tree = cKDTree(df[['Latitude', 'Longitude']])
        
        # Function to calculate density value for a single row
        def calculate_density(row):
            try:
                # Find indices of nearest neighbors within a certain radius (e.g., grid_size / 2)
                num_neighbors = len(tree.query_ball_point([row['Latitude'], row['Longitude']], grid_size / 2))
                
                # Calculate density value
                lat_index = np.digitize(row['Latitude'], lat_bins) - 1
                lon_index = np.digitize(row['Longitude'], lon_bins) - 1
                density_value = round(num_neighbors / hist[lat_index, lon_index], 6)
                
                return density_value
            except Exception as e:
                logging.error(f"Error calculating density for row: {row}, error: {e}")
                return np.nan  # Return NaN if an error occurs for this row
        
        # Apply the function to each row in the DataFrame to calculate density values
        density_values = df.apply(calculate_density, axis=1)

        # Return the calculated density values as a Series with the same index as the input DataFrame
        return density_values.astype(np.float64)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return pd.Series()  # Return empty Series in case of error




def create_engine_and_tables(file_path_1, file_path_2, database_url):
    """
    Create a database engine and multiple table schemas from a CSV file.

    Parameters:
    file_path_1 (str): The path to the CSV file containing the overall data.
    file_path_2 (str): The path to the CSV file containing the FSA-summarized data.
    
    database_url (str): The database URL for creating the SQLAlchemy engine.

    Returns:
    None
    """
    try:
        # Create engine
        engine = create_engine(database_url)

        # Load data from CSV
        df = pd.read_csv(file_path_1)
        
        # Check for empty DataFrame
        if df.empty:
            logging.error("DataFrame is empty.")
            return

        # Calculate density column
        df['Density'] = calculate_density_column(df)
        
        df2 = pd.read_csv(file_path_2)

        # Define the columns for each table
        map_table_columns = [
            'Forward_Sortation_Area', 'confirmationNo', 'startDate', 'endDate', 'Latitude', 'Longitude', 'formattedAddress',
            'postalCode', 'owner', 'contractor', 'Vermiculite', 'Piping', 'Drywall', 'Insulation',
            'Tiling', 'Floor_Tiles', 'Ceiling_Tiles', 'Ducting', 'Plaster', 'Stucco_Stipple', 'Fittings', 'Density'
        ]
        
        data_table_columns = [
            'confirmationNo', 'startDate', 'endDate','formattedAddress', 'supportDescription', 'owner', 'contractor', 'Vermiculite',
            'Piping', 'Drywall', 'Insulation', 'Tiling', 'Floor_Tiles', 'Ceiling_Tiles',
            'Ducting', 'Plaster', 'Stucco_Stipple', 'Fittings', 'Forward_Sortation_Area'
        ]
        

        # Create or replace general table
        df.to_sql('asbestos_data', engine, index=False, if_exists='replace', method='multi')
        
        # Create or replace special tables
        df[map_table_columns].to_sql('map_table', engine, index=False, if_exists='replace', method='multi')
        df[data_table_columns].to_sql('data_table', engine, index=False, if_exists='replace', method='multi')
        
        df2.to_sql('aggregated_fsa_table', engine, index=False, if_exists='replace', method='multi')
        
        logging.info("Tables created and data inserted successfully.")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except SQLAlchemyError as e:
        logging.error(f"An error occurred with the database: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def main():
    """
    Main function to handle the workflow of creating database tables from a CSV file.

    Parameters:
    None

    Returns:
    None
    """
    # Get database URL and file paths from configuration
    DATABASE_URL = get_database_url()
    
    file_path_1 = get_csv_file_path_1()
    file_path_2 = get_csv_file_path_2()

    create_engine_and_tables(file_path_1, file_path_2, DATABASE_URL)

if __name__ == '__main__':
    main()
