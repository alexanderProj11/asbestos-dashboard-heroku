import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def read_excel_file(file_path):
    # Read the Excel file into a DataFrame
    return pd.read_excel(file_path)

def create_tables(conn):
    # Cursor to execute database operations
    cur = conn.cursor()
    
    # SQL commands to create each table
    commands = [
        """
        CREATE TABLE IF NOT EXISTS raw_asbestos_data (
            Forward_Sortation_Area VARCHAR(255),
            confirmationNo VARCHAR(255),
            Latitude DOUBLE PRECISION,
            Longitude DOUBLE PRECISION,
            formattedAddress VARCHAR(255),
            postalCode VARCHAR(255),
            errorMessage VARCHAR(255),
            supportDescription VARCHAR(255),
            riskType VARCHAR(255),
            submittedDate DATE,
            startDate DATE,
            endDate DATE,
            owner VARCHAR(255),
            ownerPhoneNumber VARCHAR(255),
            contractor VARCHAR(255),
            siteContact VARCHAR(255),
            contactPhoneNumber VARCHAR(255),
            compName VARCHAR(255),
            compPhoneNumber VARCHAR(255),
            Vermiculite BOOLEAN,
            Piping BOOLEAN,
            Drywall BOOLEAN,
            Insulation BOOLEAN,
            Tiling BOOLEAN,
            Floor_Tiles BOOLEAN,
            Ceiling_Tiles BOOLEAN,
            Ducting BOOLEAN,
            Plaster BOOLEAN,
            Stucco_Stipple BOOLEAN,
            Fittings BOOLEAN
        );""",
        """
        CREATE TABLE IF NOT EXISTS map_table (
            Forward_Sortation_Area VARCHAR(255),
            confirmationNo VARCHAR(255),
            Latitude DOUBLE PRECISION,
            Longitude DOUBLE PRECISION,
            formattedAddress VARCHAR(255),
            postalCode VARCHAR(255),
            startDate DATE,
            contractor VARCHAR(255),
            Vermiculite BOOLEAN,
            Piping BOOLEAN,
            Drywall BOOLEAN,
            Insulation BOOLEAN,
            Tiling BOOLEAN,
            Floor_Tiles BOOLEAN,
            Ceiling_Tiles BOOLEAN,
            Ducting BOOLEAN,
            Plaster BOOLEAN,
            Stucco_Stipple BOOLEAN,
            Fittings BOOLEAN
        );""",
        """
        CREATE TABLE IF NOT EXISTS data_table (
            Forward_Sortation_Area VARCHAR(255),
            confirmationNo VARCHAR(255),
            Latitude DOUBLE PRECISION,
            Longitude DOUBLE PRECISION,
            formattedAddress VARCHAR(255),
            postalCode VARCHAR(255),
            startDate DATE,
            contractor VARCHAR(255),
            Vermiculite BOOLEAN,
            Piping BOOLEAN,
            Drywall BOOLEAN,
            Insulation BOOLEAN,
            Tiling BOOLEAN,
            Floor_Tiles BOOLEAN,
            Ceiling_Tiles BOOLEAN,
            Ducting BOOLEAN,
            Plaster BOOLEAN,
            Stucco_Stipple BOOLEAN,
            Fittings BOOLEAN
        );""",
        """
        CREATE TABLE IF NOT EXISTS chart_table (
            Forward_Sortation_Area VARCHAR(255),
            confirmationNo VARCHAR(255),
            Latitude DOUBLE PRECISION,
            Longitude DOUBLE PRECISION,
            formattedAddress VARCHAR(255),
            contractor VARCHAR(255),
            Vermiculite BOOLEAN,
            Piping BOOLEAN,
            Drywall BOOLEAN,
            Insulation BOOLEAN,
            Tiling BOOLEAN,
            Floor_Tiles BOOLEAN,
            Ceiling_Tiles BOOLEAN,
            Ducting BOOLEAN,
            Plaster BOOLEAN,
            Stucco_Stipple BOOLEAN,
            Fittings BOOLEAN
        );"""
    ]

    for command in commands:
        cur.execute(command)

    # Commit changes and close the connection
    conn.commit()
    cur.close()

def insert_data(df, table_name, engine):
    # Insert data into the table
    df.to_sql(table_name, engine, if_exists='append', index=False)

def main():
    # Database URL from the environment variables provided by Heroku
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Connect to the PostgreSQL database server using the Heroku URL
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    
    # Create tables
    create_tables(conn)
    
    # Close the connection
    conn.close()

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Path to your Excel file
    file_path = 'addresses_ALL-VALID_27-05-2024.xlsx'
    
    # Read Excel file
    df = read_excel_file(file_path)

    # Prepare and insert data into each table
    # Adjust DataFrame for 'raw_asbestos_data'
    df_raw_asbestos_data = df[
        [column for column in df.columns if column in {
            'Forward_Sortation_Area', 'confirmationNo', 'inputAddress', 'verdict',
            'Latitude', 'Longitude', 'formattedAddress', 'postalCode', 'errorMessage',
            'supportDescription', 'riskType', 'submittedDate', 'startDate', 'endDate',
            'owner', 'ownerPhoneNumber', 'contractor', 'siteContact', 'contactPhoneNumber',
            'compName', 'compPhoneNumber', 'Vermiculite', 'Piping', 'Drywall', 'Insulation',
            'Tiling', 'Floor_Tiles', 'Ceiling_Tiles', 'Ducting', 'Plaster', 'Stucco_Stipple',
            'Fittings'
        }]
    ].copy()

    df_data_table = df[
        [column for column in df.columns if column in {'Forward_Sortation_Area', 'confirmationNo', 'Latitude', 'Longitude',
        'formattedAddress', 'postalCode', 'startDate', 'contractor', 'Vermiculite',
        'Piping', 'Drywall', 'Insulation', 'Tiling', 'Floor_Tiles', 'Ceiling_Tiles',
        'Ducting', 'Plaster', 'Stucco_Stipple', 'Fittings'}]
    ].copy()

    df_chart_table = df[
        [column for column in df.columns if column in {'Forward_Sortation_Area', 'confirmationNo', 'Latitude', 'Longitude',
        'formattedAddress', 'contractor', 'Vermiculite', 'Piping', 'Drywall',
        'Insulation', 'Tiling', 'Floor_Tiles', 'Ceiling_Tiles', 'Ducting', 'Plaster',
        'Stucco_Stipple', 'Fittings'}]
    ].copy()

    # Example for 'map_table'
    df_map_table = df[
        [column for column in df.columns if column in {'Forward_Sortation_Area', 'confirmationNo', 'Latitude', 'Longitude',
        'formattedAddress', 'postalCode', 'startDate', 'contractor', 'Vermiculite',
        'Piping', 'Drywall', 'Insulation', 'Tiling', 'Floor_Tiles', 'Ceiling_Tiles',
        'Ducting', 'Plaster', 'Stucco_Stipple', 'Fittings'}]
    ].copy()

    # Insert data into the tables
    insert_data(df_raw_asbestos_data, 'raw_asbestos_data', engine)
    insert_data(df_map_table, 'map_table', engine)
    insert_data(df_data_table, 'data_table', engine)
    insert_data(df_chart_table, 'chart_table', engine)

if __name__ == '__main__':
    main()
