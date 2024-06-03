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

# Fetch data function with error handling
def fetch_data(table_name):
    try:
        query = f'SELECT * FROM {table_name}'
        df = pd.read_sql_query(query, con=engine)
        return df
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

# Create chart function
def create_chart(df, selected_area, selected_condition):
    if df.empty:
        return px.bar(title="No data available")

    df = df[df[selected_condition] == 1]  # Filter rows based on selected condition

    df = df.sort_values('Forward Sortation Area')

    if selected_condition not in df.columns:
        df[selected_condition] = 0

    if selected_condition == "All Notifications":
        count_df = df.groupby('Forward Sortation Area').size().reset_index(name='Counts')
    else:
        condition_counts = df.groupby('Forward Sortation Area').size().reset_index(name='Condition Counts')
        total_counts = df.groupby('Forward Sortation Area').size().reset_index(name='Total Counts')
        count_df = pd.merge(total_counts, condition_counts, on='Forward Sortation Area', how='left')
        count_df['Condition Counts'].fillna(0, inplace=True)
        count_df['Condition Percentage'] = (count_df['Condition Counts'] / count_df['Total Counts']) * 100

    if selected_area not in count_df['Forward Sortation Area'].values:
        return px.bar(title="No data available for the selected area")

    title_text = "Total Notifications per Area" if selected_condition == "All Notifications" else f"Percentage of {selected_condition} per Area"
    area_value = count_df.loc[count_df['Forward Sortation Area'] == selected_area, 'Counts'].iloc[0] if selected_condition == "All Notifications" else count_df.loc[count_df['Forward Sortation Area'] == selected_area, 'Condition Percentage'].iloc[0]
    title = f"{title_text} for {selected_area}: {area_value}"

    count_df['Highlight'] = count_df['Forward Sortation Area'].apply(lambda x: 'Selected' if x == selected_area else 'Other')
    color_discrete_map = {'Selected': 'red', 'Other': 'blue'}

    fig = px.bar(count_df, x='Forward Sortation Area', y='Counts' if selected_condition == "All Notifications" else 'Condition Percentage',
                 title=title, color='Highlight', color_discrete_map=color_discrete_map)

    fig.update_layout(showlegend=False)
    return fig

def create_table(df, selected_condition):
    if df.empty:
        return []

    df = df[df[selected_condition] == 1]  # Filter rows based on selected condition

    datetime_columns = ['startDate', 'endDate']

    for col in datetime_columns:
        if (col in df.columns) and (not df[col].isnull().all()):
            df[col] = pd.to_datetime(df[col]).dt.date

    return df.to_dict('records')

def create_map(df, selected_area, selected_condition):
    if df.empty:
        return px.scatter_mapbox(title="No data available")

    df = df[df[selected_condition] == 1]  # Filter rows based on selected condition

    if selected_area == "All Areas":
        filtered_df = df
    else:
        filtered_df = df[df['Forward Sortation Area'] == selected_area]

    if filtered_df.empty:
        return px.scatter_mapbox(title="No data available for the selected area")

    center_lat = filtered_df['Latitude'].median()
    center_lon = filtered_df['Longitude'].median()

    fig = px.scatter_mapbox(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        color='Condition',
        hover_name='contractor',
        hover_data={'formattedAddress': True, 'startDate': True, 'postalCode': True, 'Latitude': False, 'Longitude': False},
        color_continuous_scale=px.colors.cyclical.IceFire,
        size_max=15,
        zoom=10,
        center={"lat": center_lat, "lon": center_lon}
    )

    fig.update_layout(
        mapbox_style="streets",
        mapbox_accesstoken=mapbox_access_token,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig

# Layout of the application
app.layout = html.Div([
    html.H1("Asbestos Abatement Dashboard"),
    dcc.Dropdown(
        id='area-dropdown',
        options=[{'label': 'All Areas', 'value': 'All Areas'}] + [{'label': i, 'value': i} for i in fetch_data('raw_asbestos_data')['Forward Sortation Area'].dropna().unique()],
        value='All Areas',
        placeholder="Select a Forward Sortation Area",
        searchable=True
    ),
    dcc.Dropdown(
        id='condition-dropdown',
        options=[{'label': condition, 'value': condition} for condition in ['Vermiculite', 'Piping', 'Drywall', 'Insulation', 'Tiling', 'Floor_Tiles', 'Ceiling_Tiles', 'Ducting', 'Plaster', 'Stucco_Stipple', 'Fittings']],
        value='Vermiculite',
        placeholder="Select Condition",
        searchable=True
    ),
    dcc.Graph(id='area-chart'),
    dcc.Graph(id='map-plot'),
    dash_table.DataTable(
        id='pivot-table',
        page_size=30,
        hidden_columns=['supportDescription', 'startDate', 'endDate'],
        style_table={'maxHeight': '300px', 'overflowY': 'auto'}
    )
])

@app.callback(
    [Output('area-chart', 'figure'), Output('map-plot', 'figure'), Output('pivot-table', 'data')],
    [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
)
def update_output(selected_area, selected_condition):
    df = fetch_data('raw_asbestos_data')

    chart = create_chart(df, selected_area, selected_condition)
    map_plot = create_map(df, selected_area, selected_condition)
    table_data = create_table(df, selected_condition)

    return chart, map_plot, table_data

if __name__ == "__main__":
    app.run_server(debug=True)
