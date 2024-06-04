# Is this script necessary?

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to close active connections
def close_active_connections():
    try:
        # Connect to your PostgreSQL database
        DATABASE_URL = os.getenv('DATABASE_URL')
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True  # Ensure the connection can execute termination commands

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Query to find and terminate active connections
        query = sql.SQL("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'postgresql-infinite-47162'
            AND pid <> pg_backend_pid();
        """)

        # Execute the query
        cur.execute(query)

        # Print confirmation
        print("All active connections have been terminated.")

        # Close communication with the database
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error closing connections: {e}")

# Call the function
if __name__ == '__main__':
    close_active_connections()
