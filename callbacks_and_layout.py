from dash import Input, Output, dcc, html, dash_table
from dash.exceptions import PreventUpdate
from utils import fetch_data, create_chart, create_map, create_table
from dash.dependencies import Input, Output
from utils import fetch_data
from config import AREA_DROPDOWN_OPTIONS, CONDITION_DROPDOWN_OPTIONS, STYLE_CONFIG

# Fetch area options
try:
    area_options = AREA_DROPDOWN_OPTIONS + [{'label': i, 'value': i} for i in fetch_data('asbestos_data')['Forward_Sortation_Area'].dropna().unique()]
except Exception as e:
    print(f"Error fetching area options: {e}")
    area_options = AREA_DROPDOWN_OPTIONS

# Define the layout for the first page
page_1_layout = html.Div(
    style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': STYLE_CONFIG['padding']},
    children=[
        html.H1("Asbestos Abatement Dashboard", style=STYLE_CONFIG['header']),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='area-dropdown',
                    options=area_options,
                    value='All Areas',
                    placeholder="Select a Forward Sortation Area",
                    searchable=True,
                    style=STYLE_CONFIG['dropdown'],
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='condition-dropdown',
                    options=CONDITION_DROPDOWN_OPTIONS,
                    value='All Conditions',
                    placeholder="Select Condition",
                    searchable=True,
                    style=STYLE_CONFIG['dropdown']
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},
            children=[
                dcc.Graph(id='area-chart', style=STYLE_CONFIG['graph'])
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},
            children=[
                dcc.RadioItems(
                    id='selected_map_type',
                    inline=True,
                    options=[{
                            "label":
                                [
                                    html.Img(src="image_files/heatmap_icon.png", height=30),
                                    html.Span("Density Heatmap", style={'font-size': 15, 'padding-left': 10}),
                                ],
                            "value": "Density Heatmap"},
                        {
                            "label":
                                [
                                    html.Img(src="image_files/choropleth_icon.png", height=30),
                                    html.Span("Choropleth Tile Map", style={'font-size': 15, 'padding-left': 10}),
                                ], 
                            "value": "Choropleth Tile Map"},
                        {
                            "label":
                                [
                                    html.Img(src="image_files/scatter_icon.png", height=30),
                                    html.Span("Point Scatter Map", style={'font-size': 15, 'padding-left': 10}),
                                ],
                            "value": "Point Scatter Map"}], 
                    labelStyle={"display": "flex", "align-items": "center"},
                ),
                dcc.Graph(id='map-plot', style=STYLE_CONFIG['graph'])
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},
            children=[
                dcc.RadioItems(
                    id='selected_table_type',
                    inline=True,
                    options=[{
                            "label":
                                [
                                    html.Img(src="image_files/circlearrows3_icon.png", height=30),
                                    html.Span("Notifications", style={'font-size': 15, 'padding-left': 10}),
                                ],
                            "value": "Notifications"},
                        {
                            "label":
                                [
                                    html.Img(src="image_files/pivot_icon.png", height=30),
                                    html.Span("Totals", style={'font-size': 15, 'padding-left': 10}),
                                ], 
                            "value": "Totals"},
                        {
                            "label":
                                [
                                    html.Img(src="image_files/percent_icon.png", height=30),
                                    html.Span("Percentages", style={'font-size': 15, 'padding-left': 10}),
                                ],
                            "value": "Percentages"}],    
                    labelStyle={"display": "flex", "align-items": "center"},
                ),
                dash_table.DataTable(
                    id='pivot-table',
                    style_table=STYLE_CONFIG['table'],
                    style_header=STYLE_CONFIG['table']['header'],
                    style_cell=STYLE_CONFIG['table']['cell'],
                    style_as_list_view=False,
                    page_size=200,
                    sort_action='native',
                    sort_mode='multi'
                )
            ]
        )
    ]
)

# Define the layout for the second page (bar chart only)
page_2_layout = html.Div(
    style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': STYLE_CONFIG['padding']},
    children=[
        html.H1("Chart", style=STYLE_CONFIG['header']),
        html.H2("Asbestos Abatement Dashboard", style=STYLE_CONFIG['header']),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='area-dropdown',
                    options=area_options,
                    value='All Areas',
                    placeholder="Select a Forward Sortation Area",
                    searchable=True,
                    style=STYLE_CONFIG['dropdown'],
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='condition-dropdown',
                    options=CONDITION_DROPDOWN_OPTIONS,
                    value='All Conditions',
                    placeholder="Select Condition",
                    searchable=True,
                    style=STYLE_CONFIG['dropdown']
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},
            children=[
                dcc.Graph(id='area-chart', style={**STYLE_CONFIG['graph'], 'height': '600px'})  # Adjust the height as needed
            ]
        )
    ]
)

# Define the layout for the third page (map only)
page_3_layout = html.Div(
    style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': STYLE_CONFIG['padding']},
    children=[
        html.H1("Map", style=STYLE_CONFIG['header']),
        html.H2("Asbestos Abatement Dashboard", style=STYLE_CONFIG['header']),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='area-dropdown',
                    options=area_options,
                    value='All Areas',
                    placeholder="Select a Forward Sortation Area",
                    searchable=True,
                    style=STYLE_CONFIG['dropdown'],
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='condition-dropdown',
                    options=CONDITION_DROPDOWN_OPTIONS,
                    value='All Conditions',
                    placeholder="Select Condition",
                    searchable=True,
                    style=STYLE_CONFIG['dropdown']
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},
            children=[
                dcc.RadioItems(
                    id='selected_map_type',
                    options=[{
                            "label":
                                [
                                    html.Img(src="image_files/heatmap_icon.png", height=30),
                                    html.Span("Density Heatmap", style={'font-size': 15, 'padding-left': 10}),
                                ],
                            "value": "Density Heatmap"},
                        {
                            "label":
                                [
                                    html.Img(src="image_files/choropleth_icon.png", height=30),
                                    html.Span("Choropleth Tile Map", style={'font-size': 15, 'padding-left': 10}),
                                ], 
                            "value": "Choropleth Tile Map"},
                        {
                            "label":
                                [
                                    html.Img(src="image_files/scatter_icon.png", height=30),
                                    html.Span("Point Scatter Map", style={'font-size': 15, 'padding-left': 10}),
                                ],
                            "value": "Point Scatter Map"}], 
                    labelStyle={"display": "flex", "align-items": "center"},
                ),                
                dcc.Graph(id='map-plot', style=STYLE_CONFIG['graph'])
            ]
        ),
    ]
)

# Define the layout for the fourth page (data table only)
page_4_layout = html.Div(
    style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': STYLE_CONFIG['padding']},
    children=[
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='area-dropdown',
                    options=area_options,
                    value='All Areas',
                    placeholder="Select a Forward Sortation Area",
                    searchable=True,
                    style=STYLE_CONFIG['dropdown'],
                )
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'marginBottom': '10px'},
            children=[
                dcc.Dropdown(
                    id='condition-dropdown',
                    options=CONDITION_DROPDOWN_OPTIONS,
                    value='All Conditions',
                    placeholder="Select Condition",
                    searchable=True,
                    style=STYLE_CONFIG['dropdown']
                )
            ]
        ),
        html.H1("Data Table", style=STYLE_CONFIG['header']),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},
            children=[
                dcc.RadioItems(
                    id='selected_table_type',
                    inline=True,
                    options=[{
                            "label":
                                [
                                    html.Img(src="image_files/circlearrows3_icon.png", height=30),
                                    html.Span("Notifications", style={'font-size': 15, 'padding-left': 10}),
                                ],
                            "value": "Notifications"},
                        {
                            "label":
                                [
                                    html.Img(src="image_files/pivot_icon.png", height=30),
                                    html.Span("Totals", style={'font-size': 15, 'padding-left': 10}),
                                ], 
                            "value": "Totals"},
                        {
                            "label":
                                [
                                    html.Img(src="image_files/percent_icon.png", height=30),
                                    html.Span("Percentages", style={'font-size': 15, 'padding-left': 10}),
                                ],
                            "value": "Percentages"}],    
                    labelStyle={"display": "flex", "align-items": "center"},
                    value="Notifications"
                ),                
                dash_table.DataTable(
                    id='pivot-table',
                    style_table=STYLE_CONFIG['table'],
                    style_header=STYLE_CONFIG['table']['header'],
                    style_cell=STYLE_CONFIG['table']['cell'],
                    style_as_list_view=False,
                    page_size=200,
                    sort_action='native',
                    sort_mode='multi',
                    row_selectable='single',
                    column_selectable='single',
                )
            ]
        )
    ]
)

# Define the main layout with navigation
app_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Home', href='/'),
        dcc.Link('Bar Chart', href='/bar-chart', style={'marginLeft': '10px'}),
        dcc.Link('Map', href='/map', style={'marginLeft': '10px'}),
        dcc.Link('Data Table', href='/data-table', style={'marginLeft': '10px'}),
    ], style={'padding': '10px', 'backgroundColor': STYLE_CONFIG['backgroundColor']}),
    html.Div(id='page-content')
])



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
        Output('area-chart', 'figure'),
        [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')],
        [Input('url', 'pathname')]
    )
    def update_chart(selected_area, selected_condition, pathname):
        if pathname not in ['/bar-chart', '/']:
            raise PreventUpdate
        try:
            df_chart = fetch_data('aggregated_fsa_table')
            chart = create_chart(df_chart, selected_area, selected_condition)
            return chart
        except Exception as e:
            print(f"Error in update_chart: {e}")
            return {}

    @app.callback(
        Output('map-plot', 'figure'),
        [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')],
        [Input('url', 'pathname')],
        [Input('selected_map_type', 'value')]
    )
    def update_map(selected_area, selected_condition, pathname, selected_map_type):
        if pathname not in ['/map', '/']:
            raise PreventUpdate
        try:
            df_map = fetch_data('map_table')
            df_map_summary = fetch_data('aggregated_fsa_table')
            map_plot = create_map(df_map, df_map_summary, selected_map_type, selected_area, selected_condition)
            return map_plot
        except Exception as e:
            print(f"Error in update_map: {e}")
            return {}

    @app.callback(
        Output('pivot-table', 'data'),
        [Input('area-dropdown', 'value'), Input('condition-dropdown', 'value')],
        [Input('url', 'pathname')],
        [Input('selected_table_type', 'value')]
    )
    def update_table(selected_area, selected_condition, pathname, selected_table_type):
        if pathname not in ['/data-table', '/']:
            raise PreventUpdate
        try:
            df_table = fetch_data('data_table')
            df_table_summary = fetch_data('aggregated_fsa_table')
            table_data = create_table(df_table, df_table_summary, selected_table_type, selected_area, selected_condition)
            return table_data
        except Exception as e:
            print(f"Error in update_table: {e}")
            return []
