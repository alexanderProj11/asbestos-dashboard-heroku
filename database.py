from sqlalchemy import create_engine
import os
import threading
import time

# Database connection setup
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
else:
    raise ValueError("DATABASE_URL environment variable not set")

try:
    # Create a SQLAlchemy engine for database connections
    engine = create_engine(
        DATABASE_URL,
        pool_size=1,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        echo=True
    )
except Exception as e:
    print(f"Error creating engine: {e}")
    engine = None

def close_idle_connections(engine, idle_timeout=1200):
    while True:
        time.sleep(idle_timeout)
        try:
            with engine.connect() as conn:
                conn.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < current_timestamp - interval '20 minutes';")
                print("Idle connections closed.")
        except Exception as e:
            print(f"Error closing idle connections: {e}")

def start_idle_connection_closer(engine):
    if engine:
        thread = threading.Thread(target=close_idle_connections, args=(engine,))
        thread.daemon = True
        thread.start()
    else:
        print("Engine is not initialized, cannot start idle connection closer.")