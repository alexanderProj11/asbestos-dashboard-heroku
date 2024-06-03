import dash
from dash import html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # Expose the server variable for deployments

# Set Mapbox token
mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
if not mapbox_access_token:
    raise ValueError("MAPBOX_ACCESS_TOKEN environment variable not set")
px.set_mapbox_access_token(mapbox_access_token)

# Database connection setup
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL)

# Fetch data function
def fetch_data(table_name):
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

    title_text = "Total Notifications per Area" if selected_condition in ["All Notifications", "All Conditions"] else f"Percentage of {selected_condition} per Area"
    
    if selected_condition == "All Notifications":
        area_value = count_df.loc[count_df['Forward_Sortation_Area'] == selected_area, 'Counts']
    elif selected_condition == "All Conditions":
        area_value = count_df.loc[count_df['Forward_Sortation_Area'] == selected_area, 'Counts']
    else:
        area_value = count_df.loc[count_df['Forward_Sortation_Area'] == selected_area, 'Condition Percentage']
    
    if not area_value.empty:
        area_value = area_value.iloc[0]
    else:
        area_value = 0
    
    title = f"{title_text} for {selected_area}: {area_value}"

    count_df['Highlight'] = count_df['Forward_Sortation_Area'].apply(lambda x: 'Selected' if x == selected_area else 'Other')
    color_discrete_map = {'Selected': 'red', 'Other': 'blue'}

    fig = px.bar(count_df, x='Forward_Sortation_Area', y='Counts' if selected_condition in ["All Notifications", "All Conditions"] else 'Condition Percentage',
                 title=title, color='Highlight', color_discrete_map=color_discrete_map)

    fig.update_layout(showlegend=False)
    return fig

def create_table(df, selected_condition):
    """Generates a DataTable from DataFrame, formatting datetime columns to show only the date."""
    if selected_condition != "All Conditions":
        df = df[df[selected_condition] == 1].copy()  # Filter based on the selected condition

    datetime_columns = ['startDate', 'endDate']

    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date

    return df.to_dict('records')

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

    fig = px.scatter_mapbox(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        hover_name='contractor',
        hover_data=['formattedAddress', 'startDate', 'postalCode'],
        size_max=15,
        zoom=10 if selected_area == "All Areas" else 12,
        center=center
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
                    page_size=30,
                    hidden_columns=['supportDescription', 'inputAddress', 'endDate', 'verdict', 'Forward_Sortation_Area', 'Latitude', 'Longitude', 'postalCode', 'siteContact', 'contactPhoneNumber', 'errorMessage', 'submittedDate', 'owner', 'ownerPhoneNumber', 'compName', 'compPhoneNumber'],
                    style_table={'maxHeight': '300px', 'overflowY': 'auto'},
                    style_header={'backgroundColor': 'white', 'color': 'black', 'fontWeight': 'bold'},  # Bold column headers
                    style_cell={'backgroundColor': '#d3d3d3', 'color': 'black'}
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
def update_output(selected_area, selected_condition):
    df = fetch_data('asbestos_data')

    chart = create_chart(df, selected_area, selected_condition)
    map_plot = create_map(df, selected_area, selected_condition)
    table_data = create_table(df, selected_condition)

    return chart, map_plot, table_data

if __name__ == "__main__":
    app.run_server(debug=True)
