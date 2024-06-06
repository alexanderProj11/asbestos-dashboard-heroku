import os
from dotenv import load_dotenv
load_dotenv()

geojson_path = 'lfsa000a16a_e.geojson'

def load_config():
    # Load environment variables from a .env file

    # Set Mapbox token for Plotly maps
    mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
    if not mapbox_access_token:
        raise ValueError("MAPBOX_ACCESS_TOKEN environment variable not set")
    return mapbox_access_token

def get_database_url():
    """
    Get the database URL from the environment variables.

    Parameters:
    None

    Returns:
    database_url (str): The database URL.
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    return DATABASE_URL

def get_csv_file_path():
    """
    Get the CSV file path from the environment variables.

    Parameters:
    None

    Returns:
    file_path (str): The CSV file path.
    """
    file_path = os.getenv('CSV_FILE_PATH')
    return file_path

# Dropdown options
AREA_DROPDOWN_OPTIONS = [{'label': 'All Areas', 'value': 'All Areas'}]
CONDITION_DROPDOWN_OPTIONS = [
    {'label': 'All Conditions', 'value': 'All Conditions'},
    {'label': 'Vermiculite', 'value': 'Vermiculite'},
    {'label': 'Piping', 'value': 'Piping'},
    {'label': 'Drywall', 'value': 'Drywall'},
    {'label': 'Insulation', 'value': 'Insulation'},
    {'label': 'Tiling', 'value': 'Tiling'},
    {'label': 'Floor Tiles', 'value': 'Floor_Tiles'},
    {'label': 'Ceiling Tiles', 'value': 'Ceiling_Tiles'},
    {'label': 'Ducting', 'value': 'Ducting'},
    {'label': 'Plaster', 'value': 'Plaster'},
    {'label': 'Stucco Stipple', 'value': 'Stucco_Stipple'},
    {'label': 'Fittings', 'value': 'Fittings'}
]

# Style configurations
STYLE_CONFIG = {
    'backgroundColor': '#d3d3d3',
    'padding': '20px',
    'header': {'color': 'black', 'textAlign': 'center'},
    'dropdown': {'backgroundColor': 'white', 'color': 'black'},
    'graph': {'backgroundColor': '#d3d3d3'},
    'table': {
        'maxHeight': '500px',
        'overflowY': 'auto',
        'header': {'backgroundColor': 'white', 'color': 'black', 'fontWeight': 'bold', 'textAlign': 'right', 'fontSize': '16px'},
        'cell': {'backgroundColor': 'white', 'color': 'black', 'border': '2px solid lightgrey', 'textAlign': 'left', 'minWidth': '90px', 'width': '180px', 'maxWidth': '500px'}
    }
}