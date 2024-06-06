from dash import Input, Output
from utils import fetch_data, create_chart, create_map, create_table
from config import custom_style_url, tileset_id
from layout import page_1_layout, page_2_layout, page_3_layout, page_4_layout
def register_callbacks(app):
    
    @app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/bar-chart':
            return page_2_layout
        elif pathname == '/map':
            return page_3_layout
        elif pathname == '/data-table':
            return page_4_layout
        else:
            return page_1_layout

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

    @app.callback(
        Output('area-chart', 'figure'),
        [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
    )
    def update_chart(selected_area, selected_condition):
        try:
            df_chart = fetch_data('chart_table')
            chart = create_chart(df_chart, selected_area, selected_condition)
            return chart
        except Exception as e:
            print(f"Error in update_chart: {e}")
            return {}

    @app.callback(
        Output('map-plot', 'figure'),
        [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
    )
    def update_map(selected_area, selected_condition):
        try:
            df_map = fetch_data('map_table')
            map_plot = create_map(df_map, selected_area, selected_condition)
            return map_plot
        except Exception as e:
            print(f"Error in update_map: {e}")
            return {}

    @app.callback(
        Output('pivot-table', 'data'),
        [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')]
    )
    def update_table(selected_area, selected_condition):
        try:
            df_table = fetch_data('data_table')
            table_data = create_table(df_table, selected_area, selected_condition)
            return table_data
        except Exception as e:
            print(f"Error in update_table: {e}")
            return []