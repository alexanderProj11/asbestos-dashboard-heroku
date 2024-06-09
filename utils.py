import pandas as pd
import plotly.express as px
from database import engine
import os
import json
from config import load_config

MAPBOX_ACCESS_TOKEN = load_config()

def filter_data(df, selected_area, selected_condition):
    """
    Filters the DataFrame based on the selected area and condition.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the data.
    selected_area (str): The area to filter by. If "All Areas", no area filtering is applied.
    selected_condition (str): The condition to filter by. If "All Conditions", no condition filtering is applied.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    try:
        filtered_df = df.copy()
        
        if selected_condition != "All Conditions":
            filtered_df = filtered_df[filtered_df[selected_condition] == 1]
        
        if selected_area != "All Areas":
            filtered_df = filtered_df[filtered_df['Forward_Sortation_Area'] == selected_area]
        
        return filtered_df
    except Exception as e:
        print(f"Error filtering data: {e}")
        return pd.DataFrame()

def fetch_data(table_name):
    """
    Fetches data from the specified table in the database.

    Parameters:
    table_name (str): The name of the table to fetch data from.

    Returns:
    pd.DataFrame: The DataFrame containing the fetched data.
    """
    query = f'SELECT * FROM {table_name}'
    try:
        return pd.read_sql_query(query, con=engine)
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()

def create_chart(df, selected_area, selected_condition):
    """
    Generates a bar chart for the selected condition or overall notification counts.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the data.
    selected_area (str): The area to filter by. If "All Areas", no area filtering is applied.
    selected_condition (str): The condition to filter by. If "All Conditions", no condition filtering is applied.

    Returns:
    plotly.graph_objs._figure.Figure: The generated bar chart.
    """
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
    fig.update_layout(showlegend=False, xaxis={'tickfont': {'size': 10}})
    
    return fig

def create_table(df, selected_area, selected_condition):
    """
    Creates a table representation of the filtered data.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the data.
    selected_area (str): The area to filter by. If "All Areas", no area filtering is applied.
    selected_condition (str): The condition to filter by. If "All Conditions", no condition filtering is applied.

    Returns:
    list: A list of dictionaries representing the filtered data.
    """
    try:
        filtered_df = filter_data(df, selected_area, selected_condition)

        datetime_columns = ['startDate', 'endDate']
        for col in datetime_columns:
            if col in filtered_df.columns:
                filtered_df[col] = pd.to_datetime(filtered_df[col]).dt.date

        return filtered_df.to_dict('records')
    except Exception as e:
        print(f"Error creating table: {e}")
        return []

def create_map(df, selected_area, selected_condition):
    """
    Creates a map visualization of the filtered data.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the data.
    selected_area (str): The area to filter by. If "All Areas", no area filtering is applied.
    selected_condition (str): The condition to filter by. If "All Conditions", no condition filtering is applied.

    Returns:
    plotly.graph_objs._figure.Figure: The generated map visualization.
    """
    try:
        if df.empty:
            return px.scatter_mapbox(title="No data available")

        filtered_df = filter_data(df, selected_area, selected_condition)

        if filtered_df.empty:
            return px.scatter_mapbox(title="No data available for the selected area")

        filtered_df['Latitude'] = pd.to_numeric(filtered_df['Latitude'], errors='coerce')
        filtered_df['Longitude'] = pd.to_numeric(filtered_df['Longitude'], errors='coerce')
        filtered_df = filtered_df.dropna(subset=['Latitude', 'Longitude'])

        if filtered_df.empty:
            return px.scatter_mapbox(title="No valid geospatial data available")

        center = {
            "lat": filtered_df['Latitude'].median(),
            "lon": filtered_df['Longitude'].median()
        }

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
        
        # Use custom Mapbox style
        custom_style_url = 'mapbox://styles/alexsala826/clx7vfhzb01f801qoh6xah2a9'  # Replace with your custom style URL
        # Load the GeoJSON file
        with open('output_geojson_manitoba_fsa.geojson') as f:
            geojson_data = json.load(f)

        fig = px.scatter_mapbox(
            filtered_df,
            lat='Latitude',
            lon='Longitude',
            hover_name='contractor',
            hover_data=['formattedAddress', 'startDate', 'postalCode', 'confirmationNo'],
            size_max=5,
            zoom=10 if selected_area == "All Areas" else 12,
            center=center,
            title=map_title,
        )

        # Adjust opacity of the scatter points
        fig.update_traces(marker={'opacity': 0.5})

        # Use custom Mapbox style
        # custom_style_url = 'mapbox://styles/alexsala826/clx7vfhzb01f801qoh6xah2a9'  # Replace with your custom style URL

        fig.update_layout(
            mapbox_style="streets",
            mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            mapbox_layers=[
                {
                    "source": geojson_data,
                    "type": "line",
                    "below": "natural-labels",
                    "opacity": 1,
                    "color": "rgba(238, 180, 180, 10)",
                }
            ]
        )
        return fig
    except Exception as e:
        print(f"Error creating map: {e}")
        return px.scatter_mapbox(title="Error creating map")