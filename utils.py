import pandas as pd
import plotly.express as px
from database import engine
import os
import time
import json
from config import load_config
import numpy as np
from scipy.spatial import cKDTree

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
    try:
        
        df_chart = df.copy()
        df_chart = df_chart[df_chart['Forward_Sortation_Area'] != 'Overall']
        
        if selected_area == "All Areas":
            if selected_condition == "All Conditions":
                title_text = "Total Notifications by Area"
            else:
                title_text = f"Percentage of Time Asbestos is found in {selected_condition} by Area"
        else:
            if selected_condition == "All Conditions":
                area_value_ttlcount = df_chart.loc[df_chart['Forward_Sortation_Area'] == selected_area, 'Total_Notifs'].values
                title_text = f"Notification Count for {selected_area}: {area_value_ttlcount[0]}"
            else:
                area_value_percent = df_chart.loc[df_chart['Forward_Sortation_Area'] == selected_area, f"{selected_condition}_Percent"].values
                title_text = f"Percentage of Time Asbestos is found in {selected_condition} for {selected_area}: {area_value_percent[0]}"
            
        chart_x_axis = 'Forward_Sortation_Area'
        chart_y_axis = 'Total_Notifs'
        if selected_condition != "All Conditions":
            chart_y_axis = f"{selected_condition}_Percent"

        df_chart['Highlight'] = df_chart['Forward_Sortation_Area'].apply(lambda x: 'Selected' if x == selected_area else 'Other')
        color_discrete_map = {'Selected': 'red', 'Other': 'blue'}
        
        # Check if the DataFrame is empty after filtering
        if df_chart.empty:
            print("No data matches the selected criteria.")
            return px.bar(title="No data available for the selected criteria.")
        
        df_chart = df_chart.sort_values(by='Forward_Sortation_Area')
        df_chart[f"{selected_condition}_Percent"] = df_chart[f"{selected_condition}_Percent"].astype(float)
        fig = px.bar(df_chart, x=chart_x_axis, y=chart_y_axis, color='Highlight', color_discrete_map=color_discrete_map, title=title_text, 
                    hover_name='Forward_Sortation_Area')
        
        
        fig.update_traces(marker_line_color='black', marker_line_width=1.2)
        fig.update_layout(showlegend=False, xaxis={'tickfont': {'size': 10}})

        return fig
    
    except Exception as e:
        print(f"Error creating chart: {e}")
        return px.bar()

def create_table(df, df2, selected_table, selected_area, selected_condition):
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
        if selected_table == "Notifications":
            filtered_df = filter_data(df, selected_area, selected_condition)
            return filtered_df.to_dict('records')
        elif selected_table == "Totals":
            total_columns = ['Forward_Sortation_Area', 'Total_Notifs', 'Total_Vermiculite', 'Total_Piping', 'Total_Drywall', 'Total_Insulation', 'Total_Tiling', 'Total_Floor_Tiles', 'Total_Ceiling_Tiles', 'Total_Ducting', 'Total_Plaster', 'Total_Stucco_Stipple', 'Total_Fittings']
            summary_df = df2[total_columns].copy()
            return summary_df.to_dict('records')
        else:
            percentage_columns = ['Forward_Sortation_Area', 'Vermiculite_Percent', 'Piping_Percent', 'Drywall_Percent', 'Insulation_Percent', 'Tiling_Percent', 'Floor_Tiles_Percent', 'Ceiling_Tiles_Percent', 'Ducting_Percent', 'Plaster_Percent', 'Stucco_Stipple_Percent', 'Fittings_Percent']
            percentage_df = df2[percentage_columns].copy()
            return percentage_df.to_dict('records')
    except Exception as e:
        print(f"Error creating table: {e}")
        return []


def create_map(df, df2, selected_map, selected_area, selected_condition):
    """
    Creates a map visualization of the filtered data.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the data.
    df2 (pd.DataFrame): The input DataFrame containing the summary data.
    selected_map (str): The selected map type ("Density Heatmap", "Choropleth Tile Map", or "Scatter Map").
    selected_area (str): The area to filter by. If "All Areas", no area filtering is applied.
    selected_condition (str): The condition to filter by. If "All Conditions", no condition filtering is applied.

    Returns:
    plotly.graph_objs._figure.Figure: The generated map visualization.
    """
    df = df.copy()
    df2 = df2.copy()
    df2 = df2[df2['Forward_Sortation_Area'] != 'Overall']
    filtered_df = filter_data(df, selected_area, selected_condition)

    # Load the GeoJSON file
    with open('GeoJSON_stuff/Polygons/output_geojson_manitoba_fsa.geojson') as f:
        geojson_data = json.load(f)

    try:
        if selected_map == "Density Heatmap":
            fig = create_density_heatmap(filtered_df, selected_area)
        elif selected_map == "Choropleth Tile Map":
            fig = create_choropleth_map(df2, geojson_data, selected_area, selected_condition)
        else:  # Scatter Map
            fig = create_scatter_map(filtered_df, geojson_data, selected_area)
                
        # Add a unique identifier to the figure's layout to force a re-render
        unique_id = time.time()  # Using current timestamp as a unique identifier
        fig.update_layout(uirevision=unique_id)
        
        return fig
    
    except Exception as e:
        print(f"Error creating map: {e}")
        return px.scatter_mapbox(title="Error creating map")

def create_density_heatmap(filtered_df, selected_area):
    center = {
        "lat": filtered_df['Latitude'].median(),
        "lon": filtered_df['Longitude'].median()
    }
    zoom = 10 if selected_area == "All Areas" else 12

    fig = px.density_mapbox(
        filtered_df, lat='Latitude', lon='Longitude',
        z='Density', radius=10, center=center, zoom=zoom, mapbox_style="carto-positron",
        hover_name='Forward_Sortation_Area'
    )
    fig.update_layout(
        mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    # Add a unique identifier to the figure's layout to force a re-render
    unique_id = time.time()  # Using current timestamp as a unique identifier
    fig.update_layout(uirevision=unique_id)
    
    return fig

def create_choropleth_map(df2, geojson_data, selected_area, selected_condition):
    choropleth_df = df2.copy()
    center = {
        "lat": 49.89106721862937,
        "lon": -97.13086449579419
    }
    zoom = 12 if selected_area == "All Areas" else 10
    color = 'Total_Notifs' if selected_condition == "All Conditions" else f"{selected_condition}_Percent"

    fig = px.choropleth_mapbox(
        choropleth_df, geojson=geojson_data, featureidkey="properties.CFSAUID",
        locations='Forward_Sortation_Area', color=color, color_continuous_scale="Viridis",
        hover_name='Forward_Sortation_Area', zoom=zoom, center=center,
        mapbox_style="carto-positron",
    )
    fig.update_layout(
        mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_layers=[{
            "source": geojson_data,
            "type": "line",
            "opacity": 1,
            "color": "rgba(238, 180, 180, 10)",
        }]
    )
    # Before returning the fig, add an annotation
    filter_info = f"Filtering by [Area: {selected_area}, Condition: {selected_condition}]"
    fig.add_annotation(
        text=filter_info,  # The text to display
        align='right',
        showarrow=False,
        xref='paper',  # 'paper' refers to the whole figure
        yref='paper',
        x=1,  # 1 is the far right of the figure
        y=1,  # 1 is the top of the figure
        bordercolor='black',
        borderwidth=1,
        bgcolor='white',
        xanchor='right',
        yanchor='top'
    )
    # Add a unique identifier to the figure's layout to force a re-render
    unique_id = time.time()  # Using current timestamp as a unique identifier
    fig.update_layout(uirevision=unique_id)
    return fig

def create_scatter_map(filtered_df, geojson_data, selected_area):
    center = {
        "lat": filtered_df['Latitude'].median(),
        "lon": filtered_df['Longitude'].median()
    }
    fig = px.scatter_mapbox(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        hover_name='contractor',
        hover_data=['formattedAddress', 'startDate', 'postalCode', 'confirmationNo'],
        size_max=5,
        zoom=12 if selected_area == "All Areas" else 14,
        center=center,
    )
    # Adjust opacity of the scatter points
    fig.update_traces(marker={'opacity': 0.75})
    fig.update_layout(
        mapbox_style="streets",
        mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_layers=[{
            "source": geojson_data,
            "type": "line",
            "below": "natural-labels",
            "opacity": 1,
            "color": "rgba(238, 180, 180, 10)",
        }]
    )
    # Add a unique identifier to the figure's layout to force a re-render
    unique_id = time.time()  # Using current timestamp as a unique identifier
    fig.update_layout(uirevision=unique_id)    
    
    return fig
