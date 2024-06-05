import os
from dotenv import load_dotenv

def load_config():
    # Load environment variables from a .env file
    load_dotenv()

    # Set Mapbox token for Plotly maps
    mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
    if not mapbox_access_token:
        raise ValueError("MAPBOX_ACCESS_TOKEN environment variable not set")
    return mapbox_access_token

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