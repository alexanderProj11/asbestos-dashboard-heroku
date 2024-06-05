import dash
from dash import html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from flask import request, jsonify
import subprocess
import requests
import threading
import time


# Load environment variables from a .env file
load_dotenv()

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # Expose the server variable for deployments

# Set Mapbox token for Plotly maps
mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
if not mapbox_access_token:
    raise ValueError("MAPBOX_ACCESS_TOKEN environment variable not set")
px.set_mapbox_access_token(mapbox_access_token)

# Database connection setup
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

# Create a SQLAlchemy engine for database connections
engine = create_engine(
    DATABASE_URL,
    pool_size=1,               # Initial number of connections in the pool
    max_overflow=10,           # Maximum number of connections to create beyond the pool_size
    pool_timeout=30,           # Timeout in seconds to get a connection from the pool
    pool_recycle=3600,         # Recycle connections every hour to avoid stale connections
    pool_pre_ping=True,        # Test connection for liveness before using it
    echo=True                  # Log all the SQL statements executed
)

""" SCALE UP FUNCTION - currently not working
# Scale up function currently not working
# Add a route to scale up the dynos
@server.route('/scale_up', methods=['POST'])

def scale_up():
    secret_token = request.headers.get('Authorization')
    if secret_token != os.getenv('SCALE_UP_SECRET_TOKEN'):
        return jsonify({"error": "Unauthorized"}), 401

    # Run the scale_up.sh script
    result = subprocess.run(['./scale_up.sh'], capture_output=True, text=True)
    return result.stdout, 200

# Function to trigger scale up
def trigger_scale_up():
    url = 'https://asbestos-dashboard-2121da576ef0.herokuapp.com/scale_up'
    headers = {'Authorization': os.getenv('SCALING_ACCESS_TOKEN')}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Dynos scaled up successfully.")
    else:
        print(f"Failed to scale up dynos: {response.text}")

"""        

# Background task to close idle connections
def close_idle_connections(engine, idle_timeout=1200):
    """
    Periodically closes idle database connections to prevent resource exhaustion.

    Args:
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine used to connect to the database.
        idle_timeout (int, optional): The interval in seconds to wait before checking for idle connections. Defaults to 1200 seconds (20 minutes).

    Returns:
        None
    """
    while True:
        time.sleep(idle_timeout)
        with engine.connect() as conn:
            conn.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < current_timestamp - interval '20 minutes';")
            print("Idle connections closed.")

# Start the background task
def start_idle_connection_closer(engine):
    """
    Starts a background thread to periodically close idle database connections.

    Args:
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine used to connect to the database.

    Returns:
        None
    """
    thread = threading.Thread(target=close_idle_connections, args=(engine,))
    thread.daemon = True
    thread.start()

# Fetch data function
def fetch_data(table_name):
    """
    Fetches all data from the specified table in the database.

    Args:
        table_name (str): The name of the table from which to fetch data.

    Returns:
        pd.DataFrame: A DataFrame containing all the data from the specified table.
                      If an error occurs, an empty DataFrame is returned.
    """
    query = f'SELECT * FROM {table_name}'
    try:
        return pd.read_sql_query(query, con=engine)
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Create chart function
def create_chart(df, selected_area, selected_condition):
    """Generates a bar chart for the selected condition or overall notification counts."""
    df = df.sort_values('Forward_Sortation_Area').copy()

    if selected_condition != "All Conditions" and selected_condition not in df.columns:
        df[selected_condition] = 0

    if selected_condition == "All Notifications":
        count_df = df.groupby('Forward_Sortation_Area').size().reset_index(name='Counts')
    elif selected_condition == "All Conditions":
        numeric_columns = df.select_dtypes(include=['number']).columns
        count_df = df[numeric_columns].groupby(df['Forward_Sortation_Area']).sum().reset_index()
        count_df['Counts'] = df.groupby('Forward_Sortation_Area').size().values
    else:
        condition_counts = df[df[selected_condition] == 1].groupby('Forward_Sortation_Area').size().reset_index(name='Condition Counts')
        total_counts = df.groupby('Forward_Sortation_Area').size().reset_index(name='Total Counts')
        count_df = pd.merge(total_counts, condition_counts, on='Forward_Sortation_Area', how='left')
        count_df['Condition Counts'] = count_df['Condition Counts'].fillna(0)
        count_df['Condition Percentage'] = (count_df['Condition Counts'] / count_df['Total Counts']) * 100

    if selected_area not in count_df['Forward_Sortation_Area'].values and selected_area != "All Areas":
        return px.bar(title="No data available for the selected area")

    if selected_area == "All Areas":
        if selected_condition == "All Conditions":
            title_text = "Total Notifications per Area"
        elif selected_condition == "Vermiculite":
            title_text = "Percentage of Time Vermiculite is Found by Area"
        else:
            title_text = f"Percentage where Asbestos found in {selected_condition} by Area"
    else:
        if selected_condition == "All Conditions":
            area_value = count_df.loc[count_df['Forward_Sortation_Area'] == selected_area, 'Counts']
            area_value = area_value.iloc[0] if not area_value.empty else 0
            title_text = f"Total Notifications in {selected_area}: <b>{area_value}</b>"
        elif selected_condition == "Vermiculite":
            area_value = count_df.loc[count_df['Forward_Sortation_Area'] == selected_area, 'Condition Percentage']
            area_value = round(area_value.iloc[0], 2) if not area_value.empty else 0
            title_text = f"Percentage where Vermiculite is Found for {selected_area}: <b>{area_value}%</b>"
        else:
            area_value = count_df.loc[count_df['Forward_Sortation_Area'] == selected_area, 'Condition Percentage']
            area_value = round(area_value.iloc[0], 2) if not area_value.empty else 0
            title_text = f"Percentage where Asbestos is Found in {selected_condition} in {selected_area}: <b>{area_value}%</b>"

    count_df['Highlight'] = count_df['Forward_Sortation_Area'].apply(lambda x: 'Selected' if x == selected_area else 'Other')
    color_discrete_map = {'Selected': 'red', 'Other': 'blue'}

    fig = px.bar(count_df, x='Forward_Sortation_Area', y='Counts' if selected_condition in ["All Notifications", "All Conditions"] else 'Condition Percentage',
                 title=title_text, color='Highlight', color_discrete_map=color_discrete_map, hover_name='Forward_Sortation_Area')
    
    # Update bar borders to be black
    fig.update_traces(marker_line_color='black', marker_line_width=1.2)
    
    fig.update_layout(showlegend=False)
    return fig

# Create table function
def create_table(df, selected_area, selected_condition):
    """Generates a DataTable from DataFrame, formatting datetime columns to show only the date."""
    filtered_df = df

    if selected_condition != "All Conditions":
        filtered_df = df[df[selected_condition] == 1].copy()  # Filter based on the selected condition

    if selected_area != "All Areas":
        filtered_df = filtered_df[filtered_df['Forward_Sortation_Area'] == selected_area].copy()

    datetime_columns = ['startDate', 'endDate']

    # Format each datetime column to date only
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date

    return filtered_df.to_dict('records')

# Create map function
def create_map(df, selected_area, selected_condition):
    if df.empty:
        return px.scatter_mapbox(title="No data available")

    # Filter rows based on selected condition
    if selected_condition != "All Conditions":
        filtered_df = df[df[selected_condition] == 1].copy()
    else:
        filtered_df = df.copy()

    # Filter the DataFrame based on the selected area
    if selected_area != "All Areas":
        filtered_df = filtered_df[filtered_df['Forward_Sortation_Area'] == selected_area].copy()

    if filtered_df.empty:
        return px.scatter_mapbox(title="No data available for the selected area")

    # Ensure that Latitude and Longitude columns are numeric
    filtered_df['Latitude'] = pd.to_numeric(filtered_df['Latitude'], errors='coerce')
    filtered_df['Longitude'] = pd.to_numeric(filtered_df['Longitude'], errors='coerce')

    # Drop rows with invalid Latitude or Longitude values
    filtered_df = filtered_df.dropna(subset=['Latitude', 'Longitude'])

    if filtered_df.empty:
        return px.scatter_mapbox(title="No valid geospatial data available")

    # Determine center for map focusing
    center = {
        "lat": filtered_df['Latitude'].median(),
        "lon": filtered_df['Longitude'].median()
    }

    # Determine the title for the map based on selected area and condition
    if selected_area == "All Areas":
        if selected_condition == "All Conditions":
            map_title = "All Areas - All Conditions"
        else:
            map_title = f"All Areas - {selected_condition}"
    else:
        if selected_condition == "All Conditions":
            map_title = f"{selected_area} - All Conditions"
        else:
            map_title = f"{selected_area} - {selected_condition}"

    fig = px.scatter_mapbox(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        hover_name='contractor',
        hover_data=['formattedAddress', 'startDate', 'postalCode'],
        size_max=15,
        zoom=10 if selected_area == "All Areas" else 12,
        center=center,
        title=map_title
    )

    fig.update_layout(
        mapbox_style="streets",
        mapbox_accesstoken=mapbox_access_token,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig

# Layout of the application with CSS styling
app.layout = html.Div(
    style={'backgroundColor': '#d3d3d3', 'padding': '20px'},  # Light grey background
    children=[
        html.H1("Asbestos Abatement Dashboard", style={'color': 'black', 'textAlign': 'center'}),
        html.Div(
            style={'backgroundColor': '#d3d3d3', 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='area-dropdown',
                    options=[{'label': 'All Areas', 'value': 'All Areas'}] + [{'label': i, 'value': i} for i in fetch_data('asbestos_data')['Forward_Sortation_Area'].dropna().unique()],
                    value='All Areas',
                    placeholder="Select a Forward Sortation Area",
                    searchable=True,
                    style={'backgroundColor': 'white', 'color': 'black'}
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': '#d3d3d3', 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='condition-dropdown',
                    options=[{'label': 'All Conditions', 'value': 'All Conditions'}] + [{'label': condition, 'value': condition} for condition in ['Vermiculite', 'Piping', 'Drywall', 'Insulation', 'Tiling', 'Floor_Tiles', 'Ceiling_Tiles', 'Ducting', 'Plaster', 'Stucco_Stipple', 'Fittings']],
                    value='All Conditions',
                    placeholder="Select Condition",
                    searchable=True,
                    style={'backgroundColor': 'white', 'color': 'black'}
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': '#d3d3d3', 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},  # Thicker white border
            children=[
                dcc.Graph(id='area-chart', style={'backgroundColor': '#d3d3d3'})
            ]
        ),
        html.Div(
            style={'backgroundColor': '#d3d3d3', 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},  # Thicker white border
            children=[
                dcc.Graph(id='map-plot', style={'backgroundColor': '#d3d3d3'})
            ]
        ),
        html.Div(
            style={'backgroundColor': '#d3d3d3', 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},  # Thicker white border
            children=[
                dash_table.DataTable(
                    id='pivot-table',
                    style_table={'maxHeight': '500px', 'overflowY': 'auto'},
                    style_header={'backgroundColor': 'white', 'color': 'black', 'fontWeight': 'bold', 'textAlign': 'right', 'fontSize': '16px'},  # Bold column headers
                    style_cell={'backgroundColor': 'white', 'color': 'black', 
                                'border': '2px solid lightgrey', 
                                'textAlign': 'left',
                                'minWidth': '90px', 'width': '180px', 'maxWidth': '500px',
                                },
                    style_as_list_view=False,
                    page_size=200,
                    sort_action='native',
                    sort_mode='multi'
                )
            ]
        )
    ]
)

# Callbacks to update the chart, map, and pivot table based on the dropdown selections
@app.callback(
    [Output('area-chart', 'figure'), Output('map-plot', 'figure'), Output('pivot-table', 'data')],
    [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
)

# Update dashboard figures
def update_output(selected_area, selected_condition):
    # df = fetch_data('asbestos_data') --- Used?
    df_map = fetch_data('map_table')
    df_chart = fetch_data('chart_table')
    df_table = fetch_data('data_table')

    chart = create_chart(df_chart, selected_area, selected_condition)
    map_plot = create_map(df_map, selected_area, selected_condition)

    table_data = create_table(df_table, selected_area, selected_condition)

    return chart, map_plot, table_data



if __name__ == "__main__":
    # Trigger scale up - Uncomment if scale up logic gets fixed.
    # trigger_scale_up()

    start_idle_connection_closer(engine)
    
    app.run_server(debug=True)
