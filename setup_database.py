import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

def create_engine_and_table(file_path, database_url):
    """Create database engine and table schema from a CSV file."""
    # Create engine
    engine = create_engine(database_url)

    # Load data from CSV
    df = pd.read_csv(file_path)

    # Use 'if_exists='replace'' to create or replace the table based on the DataFrame's schema
    # This allows dynamic table creation based on CSV structure
    try:
        df.to_sql('asbestos_data', engine, index=False, if_exists='replace', method='multi')
        print("Table created and data inserted successfully.")
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")

def main():
    """Main function to handle workflow."""
    # Database URL from the environment variables provided by Heroku
    DATABASE_URL = os.getenv("DATABASE_URL")
    file_path = 'all_Valid_Addresses.csv'  # Ensure the file name matches your actual file

    create_engine_and_table(file_path, DATABASE_URL)

if __name__ == '__main__':
    main()
