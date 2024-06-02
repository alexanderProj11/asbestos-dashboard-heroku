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

def create_comprehensive_pivot_table(df, engine):
    """Creates and stores the comprehensive pivot table in the database."""
    # Create a comprehensive pivot table, assuming aggregating with sum
    pivot_table = df.groupby('Forward Sortation Area').sum().reset_index()
    pivot_table.to_sql('comprehensive_pivot', con=engine, if_exists='replace', index=False)
    print("Comprehensive pivot table created and stored in database.")

def main():
    file_path = 'addresses_ALL-VALID_27-05-2024.xlsx'
    try:
        # Read the Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Ensure all expected columns are present
        expected_columns = ['Vermiculite', 'Piping', 'Drywall', 'Tiling', 'Floor Tiles', 'Ceiling Tiles', 'Insulation', 'Ducting', 'Stucco/Stipple', 'Forward Sortation Area', 'Latitude', 'Longitude']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 0

        # Populate the raw_asbestos_data table
        df.to_sql('raw_asbestos_data', con=engine, if_exists='replace', index=False)
        print("raw_asbestos_data table created and populated in the database.")

        # Create and store the comprehensive_pivot table
        create_comprehensive_pivot_table(df, engine)
    except Exception as e:
        print(f"Failed to process the Excel file: {e}")

if __name__ == "__main__":
    main()
