import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging
from config import get_database_url, get_csv_file_path_1, get_csv_file_path_2, get_csv_file_path_3

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_engine_and_tables(file_path_1, file_path_2, database_url):
    """
    Create a database engine and multiple table schemas from a CSV file.

    Parameters:
    file_path_1 (str): The path to the CSV file containing the overall data.
    file_path_2 (str): The path to the CSV file containing the FSA-summarized data.
    file_path_3 (str): The path to the CSV file containing the FSA percentage data.
    database_url (str): The database URL for creating the SQLAlchemy engine.

    Returns:
    None
    """
    try:
        # Create engine
        engine = create_engine(database_url)

        # Load data from CSV
        df = pd.read_csv(file_path_1)
        df2 = pd.read_csv(file_path_2)

        # Define the columns for each table
        map_table_columns = [
            'Forward_Sortation_Area', 'confirmationNo', 'startDate', 'endDate', 'Latitude', 'Longitude', 'formattedAddress',
            'postalCode', 'owner', 'contractor', 'Vermiculite', 'Piping', 'Drywall', 'Insulation',
            'Tiling', 'Floor_Tiles', 'Ceiling_Tiles', 'Ducting', 'Plaster', 'Stucco_Stipple', 'Fittings'
        ]
        
        data_table_columns = [
            'confirmationNo', 'startDate', 'endDate','formattedAddress', 'supportDescription', 'owner', 'contractor', 'Vermiculite',
            'Piping', 'Drywall', 'Insulation', 'Tiling', 'Floor_Tiles', 'Ceiling_Tiles',
            'Ducting', 'Plaster', 'Stucco_Stipple', 'Fittings', 'Forward_Sortation_Area'
        ]
        
        chart_table_columns = [
            'Forward_Sortation_Area', 'startDate', 'confirmationNo', 'Vermiculite', 'Piping', 'Drywall',
            'Insulation', 'Tiling', 'Floor_Tiles', 'Ceiling_Tiles', 'Ducting', 'Plaster',
            'Stucco_Stipple', 'Fittings'
        ]

        # Create or replace general table
        df.to_sql('asbestos_data', engine, index=False, if_exists='replace', method='multi')
        
        # Create or replace special tables
        df[map_table_columns].to_sql('map_table', engine, index=False, if_exists='replace', method='multi')
        df[data_table_columns].to_sql('data_table', engine, index=False, if_exists='replace', method='multi')
        df[chart_table_columns].to_sql('chart_table', engine, index=False, if_exists='replace', method='multi')
        
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