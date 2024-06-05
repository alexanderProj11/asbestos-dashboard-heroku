from dash import Input, Output
from utils import fetch_data, create_chart, create_map, create_table

def register_callbacks(app):
    @app.callback(
        [Output('area-chart', 'figure'), Output('map-plot', 'figure'), Output('pivot-table', 'data')],
        [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
    )
    def update_output(selected_area, selected_condition):
        try:
            # Fetch all necessary data at once
            df = fetch_data('asbestos_data') 

            # Filter data for each component
            df_map = df[df['table_type'] == 'map_table']
            df_chart = df[df['table_type'] == 'chart_table']
            df_table = df[df['table_type'] == 'data_table']

            # Create components
            chart = create_chart(df_chart, selected_area, selected_condition)
            map_plot = create_map(df_map, selected_area, selected_condition)
            table_data = create_table(df_table, selected_area, selected_condition)

            return chart, map_plot, table_data
        except Exception as e:
            print(f"Error in update_output callback: {e}")
            return {}, {}, []