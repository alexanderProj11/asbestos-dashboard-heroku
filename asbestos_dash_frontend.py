import dash
from dash import html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()


# Initialize the Dash app
app = dash.Dash(__name__)

# Set Mapbox token
mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
px.set_mapbox_access_token(mapbox_access_token)

# Database connection setup
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def fetch_data(table_name):
    """ Utility to fetch data from a specified table in the PostgreSQL database. """
    query = f'SELECT * FROM {table_name}'
    return pd.read_sql_query(query, con=engine)

def create_chart(df, selected_area, selected_condition):
    """ Generates a bar chart for the selected condition or overall notification counts. """
    # Ensure Forward Sortation Areas are sorted alphabetically
    df = df.sort_values('Forward Sortation Area')

    # Determine if 'selected_condition' is a valid column, assume binary presence with '1' as present
    if selected_condition not in df.columns:
        df[selected_condition] = 0  # Assign zero if column is missing

    # Calculate counts or percentages based on the selected condition
    if selected_condition == "All Notifications":
        # Count total notifications per area
        count_df = df.groupby('Forward Sortation Area').size().reset_index(name='Counts')
    else:
        # Calculate the percentage of notifications with the selected condition
        condition_counts = df[df[selected_condition] == 1].groupby('Forward Sortation Area').size().reset_index(name='Condition Counts')
        total_counts = df.groupby('Forward Sortation Area').size().reset_index(name='Total Counts')
        count_df = pd.merge(total_counts, condition_counts, on='Forward Sortation Area', how='left')
        count_df['Condition Counts'].fillna(0, inplace=True)  # Replace NaN with 0
        count_df['Condition Percentage'] = (count_df['Condition Counts'] / count_df['Total Counts']) * 100

    # Handle case where selected area might not be present
    if selected_area not in count_df['Forward Sortation Area'].values:
        return px.bar(title="No data available for the selected area")

    # Title for the chart
    title_text = "Total Notifications per Area" if selected_condition == "All Notifications" else f"Percentage of {selected_condition} per Area"
    area_value = count_df.loc[count_df['Forward Sortation Area'] == selected_area, 'Counts'].iloc[0] if selected_condition == "All Notifications" else count_df.loc[count_df['Forward Sortation Area'] == selected_area, 'Condition Percentage'].iloc[0]
    title = f"{title_text} for {selected_area}: {area_value}"

    # Create 'Highlight' column for color coding
    count_df['Highlight'] = count_df['Forward Sortation Area'].apply(lambda x: 'Selected' if x == selected_area else 'Other')
    color_discrete_map = {'Selected': 'red', 'Other': 'blue'}

    # Plotting the data with dynamic title
    fig = px.bar(count_df, x='Forward Sortation Area', y='Counts' if selected_condition == "All Notifications" else 'Condition Percentage',
                 title=title, color='Highlight', color_discrete_map=color_discrete_map)

    fig.update_layout(showlegend=False)
    return fig

def create_map(df, selected_area, map_type):
    # Filtering the DataFrame based on the selected area
    filtered_df = df if selected_area == "All Areas" else df[df['Forward Sortation Area'] == selected_area]

    # Determine center for map focusing
    center = {"lat": filtered_df['Latitude'].median(), "lon": filtered_df['Longitude'].median()} if not filtered_df.empty else {"lat": 0, "lon": 0}

    # Create the scatter mapbox plot or heatmap based on selected type
    if map_type == 'scatter':
        fig = px.scatter_mapbox(
            filtered_df,
            lat='Latitude',
            lon='Longitude',
            color='Condition',  # Assuming condition coloring
            hover_name='contractor',
            hover_data=['formattedAddress', 'startDate', 'postalCode'],
            color_continuous_scale=px.colors.cyclical.IceFire,
            size_max=15,
            zoom=10 if selected_area == "All Areas" else 12,
            center=center
        )
    elif map_type == 'heatmap':
        fig = px.density_mapbox(
            filtered_df,
            lat='Latitude',
            lon='Longitude',
            z='Condition',  # Assuming a numeric measure for heatmap intensity
            radius=30,  # Adjust radius for heat point spread
            center=center,
            zoom=10 if selected_area == "All Areas" else 12,
            mapbox_style="streets"
        )

    # Common map settings
    fig.update_layout(
        mapbox_style="streets",
        mapbox_accesstoken=mapbox_access_token,
        margin={"r":0, "t":0, "l":0, "b":0}
    )
    return fig

def create_table(df):
    """
    Generates a DataTable from DataFrame, formatting datetime columns to show only the 
    date.
    """
    # List of datetime columns to format, adjust as necessary
    datetime_columns = ['startDate', 'endDate']

    # Format each datetime column to date only
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date

    return df.to_dict('records')

# Layout of the application
app.layout = html.Div([
    html.H1("Asbestos Abatement Dashboard"),
    dcc.Dropdown(
        id='area-dropdown',
        options=[{'label': 'All Areas', 'value': 'All Areas'}] + [{'label': i, 'value': i} for i in fetch_data('coordinates')['Forward Sortation Area'].unique()],
        value='All Areas',
        placeholder="Select a Forward Sortation Area",
        searchable=True
    ),
    dcc.Dropdown(
        id='condition-dropdown',
        options=[{'label': condition, 'value': condition} for condition in ['Vermiculite', 'Piping', 'Drywall', 'Tiling', 'Floor Tiles', 'Ceiling Tiles', 'Insulation', 'Ducting', 'Stucco/Stipple']],
        value='Vermiculite',
        placeholder="Select Condition",
        searchable=True
    ),
    dcc.Graph(id='area-chart'),
    dcc.Graph(id='map-plot'),
    dash_table.DataTable(
        id='pivot-table',
        page_size=30,  # Number of rows visible per page
        hidden_columns=['supportDescription', 'startDate', 'endDate'],
        style_table={'maxHeight': '300px', 'overflowY': 'auto'}  # Adjust 'maxHeight' as needed
    )
])

# Callbacks to update the chart, map, and pivot table based on the dropdown selections
@app.callback(
    [Output('area-chart', 'figure'), Output('map-plot', 'figure'), Output('pivot-table', 'data')],
    [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
)
def update_output(selected_area, selected_condition):
    df = fetch_data('comprehensive_pivot')  # Fetching the comprehensive data

    chart = create_chart(df, selected_area, selected_condition)
    map_plot = create_map(df, selected_area, 'scatter')
    table_data = create_table(df)

    return chart, map_plot, table_data

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))  # Get the port from the environment variable or default to 8050
    app.run_server(debug=True, host='0.0.0.0', port=port)
