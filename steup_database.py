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

        expected_columns = ['Vermiculite', 'Piping', 'Drywall', 'Tiling', 'Floor Tiles', 'Ceiling Tiles', 'Insulation', 'Ducting', 'Stucco/Stipple', 'Forward Sortation Area', 'Latitude', 'Longitude']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 0

        df.to_sql('raw_asbestos_data', con=engine, if_exists='replace', index=False)
        print("raw_asbestos_data table created and populated in the database.")

        # Exclude datetime columns and other non-numeric columns from the pivot table calculation
        non_numeric_columns = ['Forward Sortation Area', 'Latitude', 'Longitude', 'startDate', 'endDate']
        numeric_columns = [col for col in df.columns if col not in non_numeric_columns]

        # Create and store the comprehensive pivot table
        pivot_table = df.groupby('Forward Sortation Area')[numeric_columns].sum().reset_index()
        pivot_table.to_sql('comprehensive_pivot', con=engine, if_exists='replace', index=False)
        print("comprehensive_pivot table created and stored in the database.")

    except Exception as e:
        print(f"Failed to process the Excel file: {e}")

if __name__ == "__main__":
    file_path = 'addresses_ALL-VALID_27-05-2024.xlsx'
    process_data(file_path)
