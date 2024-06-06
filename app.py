from dash import Dash
from config import load_config
from database import engine, start_idle_connection_closer
from layout import app_layout
from callbacks import register_callbacks
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Load configuration
    load_config()

    # Initialize the Dash app
    app = Dash(__name__, suppress_callback_exceptions=True)
    server = app.server  # Expose the server variable for deployments

    # Set the layout
    app.layout = app_layout

    # Register callbacks
    register_callbacks(app)

    # MAIN ENTRY POINT
    if __name__ == "__main__":
        start_idle_connection_closer(engine)
        app.run_server(debug=True)

except Exception as e:
    logging.error(f"An error occurred: {e}")