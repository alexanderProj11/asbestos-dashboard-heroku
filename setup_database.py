import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def create_table(conn):
    """Create a single table in the PostgreSQL database."""
    command = """
        CREATE TABLE IF NOT EXISTS asbestos_data (
            Forward_Sortation_Area VARCHAR(255),
            confirmationNo VARCHAR(255),
            inputAddress VARCHAR(255),
            verdict VARCHAR(255),
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
        );
    """
    cur = conn.cursor()
    cur.execute(command)
    conn.commit()
    cur.close()

def insert_data(df, engine):
    """Insert data into the specified table."""
    df.to_sql('asbestos_data', engine, if_exists='append', index=False)

def query_data(conn):
    """Query and print data from the specified table to verify correctness."""
    cur = conn.cursor()
    cur.execute('SELECT "confirmationNo", "latitude", "longitude" FROM "asbestos_data"')
    rows = cur.fetchall()
    print("Data from asbestos_data:")
    for row in rows:
        print(f"ConfirmationNo: {row[0]}, Latitude: {row[1]}, Longitude: {row[2]}")
    cur.close()

def main():
    """Main function to handle workflow."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    create_table(conn)

    engine = create_engine(DATABASE_URL)
    file_path = 'all_Valid_Addresses.csv'
    df = pd.read_csv(file_path)

    insert_data(df, engine)
    query_data(conn)

    conn.close()

if __name__ == '__main__':
    main()