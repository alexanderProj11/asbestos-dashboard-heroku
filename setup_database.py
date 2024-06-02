import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection setup
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
engine = create_engine(DATABASE_URL)

def process_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')

        df.to_sql('raw_asbestos_data', con=engine, if_exists='replace', index=False)
        print("raw_asbestos_data table created and populated in the database.")


    except Exception as e:
        print(f"Failed to process the Excel file: {e}")

if __name__ == "__main__":
    file_path = 'addresses_ALL-VALID_27-05-2024.xlsx'
    process_data(file_path)
