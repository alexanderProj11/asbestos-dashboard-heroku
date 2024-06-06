from dash import html, dcc, dash_table
from dash import Dash, Input, Output, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
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
                dcc.Graph(id='map-plot', style=STYLE_CONFIG['graph'])
            ]
        ),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},
            children=[
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
                dcc.Graph(id='area-chart', style={**STYLE_CONFIG['graph'], 'height': '800px'})  # Adjust the height as needed
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
                dcc.Graph(id='map-plot', style=STYLE_CONFIG['graph'])
            ]
        ),
    ]
)

# Define the layout for the fourth page (data table only)
page_4_layout = html.Div(
    style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': STYLE_CONFIG['padding']},
    children=[
        html.H1("Table", style=STYLE_CONFIG['header']),
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
        html.H1("Data Table", style=STYLE_CONFIG['header']),
        html.Div(
            style={'backgroundColor': STYLE_CONFIG['backgroundColor'], 'padding': '10px', 'border': '3px solid white', 'marginBottom': '10px'},
            children=[
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
