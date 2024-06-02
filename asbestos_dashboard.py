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
    return pd.read_sql_query(query, con=engine)

# Create chart function
def create_chart(df, selected_area, selected_condition):
    """Generates a bar chart for the selected condition or overall notification counts, with dynamic title adjustments and sorting."""
    # Sorting Forward Sortation Areas alphabetically
    df = df.copy()
    df['Forward Sortation Area'] = pd.Categorical(df['Forward Sortation Area'], categories=sorted(df['Forward Sortation Area'].unique()), ordered=True)

    if selected_condition not in df.columns:
        df[selected_condition] = 0  # Add missing condition with default zero

    if selected_condition == "All Notifications":
        # Count total notifications per area
        count_df = df.groupby('Forward Sortation Area', observed=False).size().reset_index(name='Counts')
    else:
        # Calculate the percentage of notifications with the selected condition
        condition_counts = df[df[selected_condition] == 1].groupby('Forward Sortation Area').size().reset_index(name='Condition Counts')
        total_counts = df.groupby('Forward Sortation Area').size().reset_index(name='Total Counts')
        count_df = total_counts.merge(condition_counts, on='Forward Sortation Area', how='left')
        count_df['Condition Counts'].fillna(0, inplace=True)
        count_df['Condition Percentage'] = (count_df['Condition Counts'] / count_df['Total Counts']) * 100

    count_df['Highlight'] = ['Selected' if x == selected_area else 'Other' for x in count_df['Forward Sortation Area']]
    color_discrete_map = {'Selected': 'red', 'Other': 'blue'}

     # Plotting the data with dynamic title
    title = ""
    if selected_condition == "All Notifications":
        title = f'Total Notifications for {selected_area}: {count_df[count_df["Forward Sortation Area"] == selected_area]["Counts"].iloc[0]}' if selected_area != "All Areas" else 'Total Notifications per Area'
        fig = px.bar(count_df, x='Forward Sortation Area', y='Counts', title=title,
                     labels={'Counts': 'Total Notifications'}, color='Highlight', color_discrete_map=color_discrete_map)
    else:
        title = f'Percentage of {selected_condition} in {selected_area}: {count_df[count_df["Forward Sortation Area"] == selected_area]["Condition Percentage"].iloc[0]:.2f}%' if selected_area != "All Areas" else f'Percentage of {selected_condition} per Area'
        fig = px.bar(count_df, x='Forward Sortation Area', y='Condition Percentage',
                     title=title,
                     labels={'Condition Percentage': f'Percentage of {selected_condition}'},
                     color='Highlight', color_discrete_map=color_discrete_map)
    
    # Add text box for selected area if it's not 'All Areas'
    if selected_area != "All Areas":
        area_value = count_df.loc[count_df['Forward Sortation Area'] == selected_area, 'Counts'].iloc[0] if selected_condition == "All Notifications" else count_df.loc[count_df['Forward Sortation Area'] == selected_area, 'Condition Percentage'].iloc[0]
        fig.add_annotation(
            x=selected_area, 
            y=area_value,
            text=f"{area_value:.2f}%" if selected_condition != "All Notifications" else f"{int(area_value)} Total",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40,
            font=dict(color='red')
        )
    
    # Explicitly defining color ordering for consistency
    fig.update_layout(showlegend=False,
        title_font=dict(family="Arial, sans-serif", size=22, color='Black'),
        xaxis=dict(
            title_font=dict(family="Arial, sans-serif", size=18, color='Black'),
            tickfont=dict(family="Raleway, sans-serif", size=12, color='DarkRed')
        ),
        yaxis=dict(
            title_font=dict(family="Arial, sans-serif", size=18, color='Black'),
            tickfont=dict(family="Raleway, sans-serif", size=12, color='DarkRed')
        )
    )
    fig.update_traces(marker_line_color='black', marker_line_width=1.5)
    return fig


def create_table(df):
    if df.empty:
        return []

    datetime_columns = ['startDate', 'endDate']

    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date

    return df.to_dict('records')


def create_map(df, selected_area):
    """
    Generates a map visualization using Mapbox, enhanced with more interactive features.

    Args:
        df (DataFrame): The dataframe containing the data to plot.
        selected_area (str): The area selected by the user, or 'All Areas' for no filtering.

    Returns:
        plotly.graph_objs._figure.Figure: A figure object containing the map.
    """
    filtered_df = df


    # Checking if there are any coordinates to plot
    if filtered_df[['Latitude', 'Longitude']].dropna().empty:
        raise ValueError("No valid latitude or longitude data to plot.")

    # Determine center only if there are points to avoid errors on empty data
    center = {"lat": filtered_df['Latitude'].median(), "lon": filtered_df['Longitude'].median()} if not filtered_df.empty and selected_area != "All Areas" else None

    # Create the scatter mapbox plot
    fig = px.scatter_mapbox(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        color=color,  # Coloring points based on the 'Condition' column
        hover_name='contractor',  # Main title for hover information
        hover_data=['formattedAddress', 'startDate', 'postalCode'],  # Additional data shown on hover
        color_continuous_scale=px.colors.cyclical.IceFire,  # Set the color scale
        size_max=15,
        zoom=9 if selected_area == "All Areas" else 11,
        center=center
    )

    # Update map layout 
    fig.update_layout(
        mapbox_style="streets",  
        mapbox_accesstoken=mapbox_access_token,
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return fig

# Layout of the application
app.layout = html.Div([
    html.H1("Asbestos Abatement Dashboard", style={'text-align': 'center'}),
    dcc.Dropdown(
        id='condition-dropdown',
        options=[
            {'label': 'All Notifications', 'value': 'All Notifications'}] + 
            [{'label': condition, 'value': condition} for condition in [
                'Vermiculite', 'Piping', 'Drywall', 'Tiling', 'Floor Tiles', 'Ceiling Tiles', 
                'Insulation', 'Ducting', 'Stucco/Stipple'
            ]],
        value='All Notifications',
        placeholder="Select Condition",
        searchable=True
    ),
    dcc.Graph(id='area-chart', style={'border': '2px solid white', 'padding': '10px'}),
    dcc.Graph(id='map-plot', style={'border': '2px solid white', 'padding': '10px'}),
    dash_table.DataTable(
        id='pivot-table', page_size=30,
        hidden_columns=['supportDescription', 'endDate', 'confirmationNo'], 
        style_table={'maxHeight': '300px', 'overflowY': 'auto'},  # Adjust 'maxHeight' as needed
        style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold',
        'color': 'black',
        'border': '1px solid black',
        'text_align': 'center'},
        style_cell={
        'backgroundColor': 'white',
        'color': 'black',
        'fontSize': 12,
        'font-family': 'Nunito, sans-serif',
        'textAlign': 'left',
        'border': '1px solid grey'
        }
        )    
], style={'backgroundColor': '#D3D3D3', 'padding': '10px'})


@app.callback(
    [Output('area-chart', 'figure'), Output('map-plot', 'figure'), Output('pivot-table', 'data')],
    [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
)
def update_output(selected_area, selected_condition):
    df = fetch_data('raw_asbestos_data')

    chart = create_chart(df, selected_area, selected_condition)
    map_plot = create_map(df, selected_area)
    table_data = create_table(df)

    return chart, map_plot, table_data

if __name__ == "__main__":
    app.run_server(debug=True)
