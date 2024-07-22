# Packages
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Local
from utils.func import importData, createSpatialVis, createMetadataTables, createStatisticsPlot
from utils.lang.en import *
from utils.design.layout import *
from utils.const import *

# Data import and preprocess 
df = importData('src/assets/data/PETERSON_FINAL.parquet')
stations = importData('src/assets/data/stationlocations.parquet')

refline = df.copy()
refline = refline[refline.file == '14322dat.txt']
refline['name'] = 'REFERENCE LINE'
df.datetime = pd.to_datetime(df.datetime)
df['water_temp'] = df['water_temp'].combine_first(df['bow_temp'])
transectDates = df.groupby('file')['datetime'].min().dt.date.astype(str).to_list()
transectDates.sort()
transectFiles = df.file.unique().tolist()

# App init
app = Dash(
    __name__,
    title = 'SF Bay Flowthrough',
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
)

# Set application layout
app.layout = (
    html.Div(className='div-body', children=[
        dbc.Navbar(children=[
            dbc.Container([
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row([
                                dbc.Col(children=html.Img(src=BRAND_LOGO, className="navbar-img"), className='nav-img-col'),
                                dbc.Col(children=dbc.NavbarBrand(headerTitle, className="navbar-title"), className='nav-title-col'),
                                dbc.Col(children=html.A(href=PETERSON_HREF, children=html.H6("ABOUT", className='nav-about')), className='nav-about-col'),
                            ],
                            align="center",
                            justify='right',
                            className="navbar-row",
                        ),
                        href=CAWSC_HREF,
                        style={"textDecoration": "none"},
                    ),
                ],
            className='navbar-container'),
        ],
            #html.Img(src=RV_PETERSON, className="navbar-peterson")],
        color="#00264C",
        dark=True,
        className="navbar drop-shadow"
        ),
        # Begin body
        dbc.Row(align='top', children=[
            dbc.Col(className='col1', children=[
            dbc.Container(className='option-container', children=[
                dbc.Card(className='option-card drop-shadow', children=[
                    dbc.Row(dbc.ModalTitle('FILTER OPTIONS', className='option-header')),
                    html.Hr(className='option-hr'),
                    dbc.Row(dbc.ModalTitle('Parameter:', className='option-modal')),
                    dcc.Dropdown(
                        options=[{'label': 'Chlorophyll', 'value': 'chlor'}, 
                                 {'label': 'Salinity', 'value': 'salinity'}, 
                                 {'label': 'Water Temperature', 'value': 'water_temp'}],
                        value='salinity',
                        placeholder='Salinity',
                        clearable=False,
                        id='param-select',
                        className='option-select',
                        style={'border-top': 'none', 
                            'border-radius': '0px',
                            'border-right': 'none'}
                    ),
                    dbc.Row(dbc.ModalTitle('Sample Size:', className='option-modal')),
                    dcc.Input(
                        type='number',
                        value=1000,
                        placeholder='1000',
                        debounce=True,
                        step=1,
                        min=1,
                        max=len(df),
                        id='sample-size',
                        className='option-select',
                        style={
                            'border-top': 'none',
                            'border-right': 'none',
                            'border-width': '1px',
                            'border-color': 'lightgrey',
                            'border-radius': '0px'
                        }
                    ),
                    dbc.Row(dbc.ModalTitle('Sample Seed:', className='option-modal')),
                    dcc.Input(
                        type='number',
                        placeholder='12345',
                        value=12345,
                        min=0,
                        max=999999999,
                        step=1,
                        debounce=True,
                        id='sample-seed',
                        className='option-select',
                        style={
                            'border-top': 'none',
                            'border-right': 'none',
                            'border-width': '1px',
                            'border-color': 'lightgrey',
                            'border-radius': '0px'
                        }
                    ),
                    dbc.Row(dbc.ModalTitle('Sample by Station:', className='option-modal')),
                    dcc.Dropdown(
                        options=STATION_IDS,
                        value=None,
                        placeholder='None selected...',
                        clearable=True,
                        multi=True,
                        id='station-select',
                        className='option-select',
                        style={'border-top': 'none', 
                            'border-radius': '0px',
                            'border-right': 'none'}
                    ),
                    dbc.Row(dbc.ModalTitle('Sample by Date:', className='option-modal')),
                    dcc.Dropdown(
                        options=transectDates,
                        value=None,
                        placeholder='None selected...',
                        id='date-select',
                        className='option-select',
                        style={'border-top': 'none', 
                            'border-radius': '0px',
                            'border-right': 'none'}
                    ),
                ])
            ]),
            dbc.Container(className='option-container', children=[
                dbc.Card(className='option-card drop-shadow', children=[
                    dbc.Row(dbc.ModalTitle('GRAPH OPTIONS', className='option-header')),
                    html.Hr(className='option-hr'),
                    dbc.Row(dbc.ModalTitle('Map Tile:', className='option-modal')),
                    dcc.Dropdown(
                        options=[{'label': 'Carto Positron (default)', 'value': 'carto-positron'},
                                 {'label': 'Carto Darkmatter', 'value': 'carto-darkmatter'},
                                 {'label': 'Open Street Map', 'value': 'open-street-map'}],
                        value='carto-positron',
                        placeholder='Carto Positron (default)',
                        clearable=False,
                        id='map-select',
                        className='option-select',
                        style={'border-top': 'none', 
                            'border-radius': '0px',
                            'border-right': 'none'}
                    ),
                    dbc.Checklist(className='station-toggle', id='station-toggle',
                                  options=[{"label": "Toggle stations", "value": 1}],
                                  value=[0],
                                  switch=True),
                    dbc.Checklist(className='station-toggle', id='ref-toggle',
                                  options=[{"label": "Toggle reference line", "value": 1}],
                                  value=[0],
                                  switch=True),
                    dbc.Checklist(className='station-toggle', id='coerce-toggle',
                                  options=[{"label": "Coerce to reference line", "value": 1}],
                                  value=[0],
                                  switch=True),
                ])
            ])
        ]),
            dbc.Container(className='map-container', fluid=True, children=[
                dbc.Card(className='map-card drop-shadow', children=[
                    dbc.Row(children=[
                        dbc.ModalTitle('TRANSECT VISUALIZATION', className='map-modal'),
                        dbc.Button("Toggle Metadata", id='metadata-button', className='metadata-button'),
                        dbc.Button("Reset Filters", id='reset-button', className='reset-button btn-danger', color='danger')
                    ]),
                    dcc.Loading(id='spatial-loading', className='spatial-loading', children=[
                        dcc.Graph(id='spatial-plot', className='spatial-plot',
                        style={'height': '70vh'},
                        config={'displayModeBar': False},
                        figure={'layout': go.Layout(xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}, 
                                                    yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}
                    )})],
                        overlay_style={"visibility":"visible", "opacity": 0.65},                        
                        parent_style={"visibility":"visible", "backgroundColor": "white"},
                        type='cube',
                        color='#00264C'
                    ),
                    dbc.Fade(className='metadata-fade', id='metadata-fade', is_in=False, children=[
                        dbc.Card(className='metadata-card', children=[
                            dbc.ModalTitle('Selection Metadata', className='metadata-modal'),
                            dbc.Table.from_dataframe(createMetadataTables(df), striped=True, bordered=True, hover=True, className='metadata-table'),
                            dbc.ModalTitle('Sample Metadata', className='metadata-modal'),
                            html.Div(id='metadata-sample')
                        ])
                    ])
                ])
            ])
        ]),
        dbc.Row(className='stats-row', children=[
            dbc.Container(className='stats-container', children=[
                dbc.Card(className='stats-card drop-shadow', children=[
                    dbc.Row(className='stats-title-row', children=[
                        dbc.ModalTitle('SELECTION STATISTICS', className='map-modal', style={'padding-left': '17px'})
                    ]),
                    dcc.Loading(id='statistical-loading', className='spatial-loading', children=[
                        dcc.Graph(id='stats-plot', className='stats-plot',
                        style={'height': '70vh'},
                        config={'displayModeBar': False},
                        figure={'layout': go.Layout(xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}, 
                                                    yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False})}
                        )],
                        overlay_style={"visibility":"visible", "opacity": 0.65},                        
                        parent_style={"visibility":"visible", "backgroundColor": "white"},
                        type='cube',
                        color='#00264C'
                    ),
                ])
            ])
        ])
    ])
)

# Callback for updating the main plot
@callback(
    Output('spatial-plot', 'figure'),
    Output('metadata-sample', 'children'),
    Output('stats-plot', 'figure'),
    Input('param-select', 'value'),
    Input('sample-size', 'value'),
    Input('sample-seed', 'value'),
    Input('station-select', 'value'),
    Input('date-select', 'value'),
    Input('map-select', 'value'),
    Input('station-toggle', 'value'),
    Input('ref-toggle', 'value'),
    Input('coerce-toggle', 'value'),
)
def update_graph_filters(param, samp_size, samp_seed, sta_select, date, mapTile, station_t, ref_t, coerce_t):
    dfg = df.copy()
    dfg.datetime = pd.to_datetime(dfg.datetime)
        # For now, sample data if not already sampled by a date to speed things up
    if not date and not sta_select: # neither
        dfg = dfg.sample(n=samp_size, random_state=samp_seed)
    elif date and not sta_select: # date, not station       
        dfg = dfg[dfg.datetime.dt.date.astype(str) == date]
    elif sta_select and not date: # station, not date
        dfg = dfg[dfg.station_id.isin(sta_select)]
    else: # both
        dfg = dfg[(dfg.station_id.isin(sta_select)) & (dfg.datetime.dt.date.astype(str) == date)]

    # Figure and tables for transect vis
    fig_transect = createSpatialVis(dfg, stations, refline, param, mapTile, station_t, ref_t, coerce_t)   
    table = dbc.Table.from_dataframe(createMetadataTables(dfg), striped=True, bordered=True, hover=True, className='metadata-table')

    # Figures for statistical vis
    fig_stats = createStatisticsPlot(dfg)

    return fig_transect, table, fig_stats

# Callback for updating sample size/seed dropdown availability
@callback(
    Output('sample-size', 'disabled'),
    Output('sample-seed', 'disabled'),
    Input('date-select', 'value'),
    Input('station-select', 'value')
)
def update_fields(date_sel, sta_select):
    if date_sel or sta_select:
        return True, True
    return False, False

# Metadata button callback
@callback(
    Output('metadata-fade', 'is_in'),
    Output('metadata-button', 'style'),
    Input('metadata-button', 'n_clicks'),
    State('metadata-fade', 'is_in')
)
def metadata_button(n, is_in):
    if not n: # metadata OFF -- page load
        style = {'background-color': '#999', 'border-color': '#00264C'}
        return False, style
    
    if n % 2 == 0: # metadata OFF
        style = {'background-color': '#999', 'border-color': '#00264C'}
        return False, style
    
    else: # metadata ON
        style = {'background-color': '#00264C', 'border-color': '#00264C'}
        return True, style

# Callback for resetting all filters and plots    
@callback(
    Output('param-select', 'value'),
    Output('sample-size', 'value'),
    Output('sample-seed', 'value'),
    Output('station-select', 'value'),
    Output('date-select', 'value'),
    Output('map-select', 'value'),
    Output('station-toggle', 'value'),
    Output('ref-toggle', 'value'),
    Output('coerce-toggle', 'value'),
    Input('reset-button', 'n_clicks'),
)
def reset_filters(n):
    return 'salinity', 1000, 12345, None, None, 'carto-positron', [0], [0], [0]
    

if __name__ == '__main__':
    app.run(debug=True)