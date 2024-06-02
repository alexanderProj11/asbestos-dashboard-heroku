import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Database connection setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)

def create_comprehensive_pivot_table(df, engine):
    """Creates and stores the comprehensive pivot table in the database."""
    # Create a comprehensive pivot table, assuming aggregating with sum
    pivot_table = df.groupby('Forward Sortation Area').sum().reset_index()
    pivot_table.to_sql('comprehensive_pivot', con=engine, if_exists='replace', index=False)
    print("Comprehensive pivot table created and stored in database.")

def process_data(file_path):
    """Processes the Excel file to update the database with asbestos data."""
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            print("File read successfully!")

            # Normalize data to ensure all expected columns are present
            expected_columns = [
                'Vermiculite', 'Piping', 'Drywall', 'Tiling', 'Floor Tiles', 'Ceiling Tiles',
                'Insulation', 'Ducting', 'Stucco/Stipple', 'Forward Sortation Area'
            ]
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = 0  # Adding missing columns as zero-filled if they're not in the source file
                    print(f"Added missing column: {col}")

            # Store the normalized data directly into the database for future reference
            df.to_sql('raw_asbestos_data', con=engine, if_exists='replace', index=False)
            print("Raw data stored in database.")

            # Create a comprehensive pivot table
            create_comprehensive_pivot_table(df, engine)

        except Exception as e:
            print(f"Failed to process the Excel file: {e}")
    else:
        print("File does not exist or is not accessible.")

def manual_update(file_path):
    """Manually triggers the data processing function."""
    print("Manual data update triggered.")
    process_data(file_path)

def periodic_check(file_path, interval=3600):
    """Periodically checks and updates the database with new data."""
    while True:
        process_data(file_path)
        print(f"Data checked and updated at {time.ctime()}.")
        time.sleep(interval)

def main():
    """
    Main function to set up the database with initial data from an Excel file.
    It ensures that the data is normalized and all necessary tables are created in the database.
    """
    file_path = 'addresses_ALL-VALID_27-05-2024.xlsx'  # Ensure this path is correct relative to the script's execution context

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print("Excel file read successfully!")

        # Normalize data to ensure all expected columns are present
        expected_columns = [
            'Vermiculite', 'Piping', 'Drywall', 'Tiling', 'Floor Tiles', 'Ceiling Tiles',
            'Insulation', 'Ducting', 'Stucco/Stipple', 'Forward Sortation Area', 'Latitude', 'Longitude'
        ]
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 0  # Adding missing columns as zero-filled if they're not in the source file
                print(f"Added missing column: {col}")

        # Store the normalized data directly into the database for future reference
        df.to_sql('raw_asbestos_data', con=engine, if_exists='replace', index=False)
        print("Raw data stored in database.")

        # Create a comprehensive pivot table
        create_comprehensive_pivot_table(df, engine)

    except Exception as e:
        print(f"Failed to process the Excel file: {e}")

if __name__ == "__main__":
    main()
