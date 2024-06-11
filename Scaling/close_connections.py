# Is this script necessary?

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to close active connections
def close_active_connections():
    """
    Terminates all active connections to a specific PostgreSQL database, except the current connection.

    This function connects to a PostgreSQL database using the connection string provided in the
    environment variable 'DATABASE_URL'. It then executes a query to terminate all active connections
    to the database named 'postgresql-infinite-47162', except for the current connection.

    Raises:
        Exception: If there is an error connecting to the database or executing the query, an exception
                   is caught and its message is printed.
    """
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