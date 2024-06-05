from dash import Input, Output
from utils import fetch_data, create_chart, create_map, create_table

def register_callbacks(app):
    @app.callback(
        [Output('area-chart', 'figure'), Output('map-plot', 'figure'), Output('pivot-table', 'data')],
        [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
    )
    def update_output(selected_area, selected_condition):
        try:
            df_map = fetch_data('map_table')
            df_chart = fetch_data('chart_table')
            df_table = fetch_data('data_table')

            chart = create_chart(df_chart, selected_area, selected_condition)
            map_plot = create_map(df_map, selected_area, selected_condition)
            table_data = create_table(df_table, selected_area, selected_condition)

            return chart, map_plot, table_data
        except Exception as e:
            print(f"Error in update_output: {e}")
            return {}, {}, []