import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def create_engine_and_tables(file_path, database_url):
    """
    Create a database engine and multiple table schemas from a CSV file.

    Parameters:
    file_path (str): The path to the CSV file containing the data.
    database_url (str): The database URL for creating the SQLAlchemy engine.

    Returns:
    None
    """
    # Create engine
    engine = create_engine(database_url)

    # Load data from CSV
    df = pd.read_csv(file_path)

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

    # Create or replace tables
    try:
        df.to_sql('asbestos_data', engine, index=False, if_exists='replace', method='multi')
        df[map_table_columns].to_sql('map_table', engine, index=False, if_exists='replace', method='multi')
        df[data_table_columns].to_sql('data_table', engine, index=False, if_exists='replace', method='multi')
        df[chart_table_columns].to_sql('chart_table', engine, index=False, if_exists='replace', method='multi')
        print("Tables created and data inserted successfully.")
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")

def main():
    """
    Main function to handle the workflow of creating database tables from a CSV file.

    Parameters:
    None

    Returns:
    None
    """
    # Database URL from the environment variables provided by Heroku
    DATABASE_URL = os.getenv("DATABASE_URL")
    file_path = 'all_Valid_Addresses.csv'  # Ensure the file name matches your actual file

    create_engine_and_tables(file_path, DATABASE_URL)

if __name__ == '__main__':
    main()