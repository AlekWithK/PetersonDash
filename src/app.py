# Packages
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd

# Local
from utils.func import importData, createSpatialVis
from utils.lang.en import *
from utils.design.layout import *
from utils.const import *

# Data import and preprocess 
df = importData('src/assets/data/PETERSON_FINAL.parquet')
stations = importData('src/assets/data/stationlocations.parquet')
refline = df[df.file == '14322dat.txt']
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
    html.Div(children=[
        dbc.Navbar(children=[
            dbc.Container([
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row([
                                dbc.Col(children=html.Img(src=BRAND_LOGO, className="navbar-img"), className='nav-img-col'),
                                dbc.Col(children=dbc.NavbarBrand(headerTitle, className="navbar-title"), className='nav-title-col'),
                                #dbc.Col(children=html.Img(src=RV_PETERSON, className="navbar-peterson"), className='nav-pet-col'),
                            ],
                            align="center",
                            className="navbar-row",
                        ),
                        href=PETERSON_HREF,
                        style={"textDecoration": "none"},
                    ),
                ],
            className='navbar-container'),
        ],
            #html.Img(src=RV_PETERSON, className="navbar-peterson")],
        color="grey",
        dark=True,
        className="navbar drop-shadow"
        ),
        # Begin body
        dbc.Row(align='top', children=[
            dbc.Col(className='col1', children=[
            dbc.Container(className='option-container', children=[
                dbc.Card(className='option-card drop-shadow', children=[
                    dbc.Row(dbc.ModalTitle('Filter Options', className='option-header')),
                    html.Hr(className='option-hr'),
                    dbc.Row(dbc.ModalTitle('Parameter', className='option-modal')),
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
                    dbc.Row(dbc.ModalTitle('Sample Size', className='option-modal')),
                    dcc.Input(
                        type='number',
                        value=10000,
                        placeholder='10000',
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
                    dbc.Row(dbc.ModalTitle('Sample Seed', className='option-modal')),
                    dcc.Input(
                        type='number',
                        placeholder='123',
                        value=123,
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
                    dbc.Row(dbc.ModalTitle('Transect by Date', className='option-modal')),
                    dcc.Dropdown(
                        options=transectDates,
                        value=None,
                        placeholder='None Selected...',
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
                    dbc.Row(dbc.ModalTitle('Graph Options', className='option-header')),
                    html.Hr(className='option-hr'),
                    dbc.Row(dbc.ModalTitle('Map Tile', className='option-modal')),
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
                    dbc.Row(dbc.ModalTitle('Transect Visualization', className='map-modal')),
                    dcc.Graph(id='spatial-plot', className='spatial-plot',
                            style={'height': '70vh'},
                            config={'displayModeBar': False})
                ])
            ])
        ])
    ])
)

# Callback for updating the main plot
@callback(
    Output('spatial-plot', 'figure'),
    Input('param-select', 'value'),
    Input('sample-size', 'value'),
    Input('sample-seed', 'value'),
    Input('date-select', 'value'),
    Input('map-select', 'value'),
    Input('station-toggle', 'value'),
    Input('ref-toggle', 'value'),
    Input('coerce-toggle', 'value'),
)
def update_graph_filters(param, samp_size, samp_seed, date, mapTile, station_t, ref_t, coerce_t):
    return createSpatialVis(df, stations, refline, param, samp_size, samp_seed, date, mapTile, station_t, ref_t, coerce_t)

# Callback for updating sample size/seed dropdown availability
@callback(
    Output('sample-size', 'disabled'),
    Output('sample-seed', 'disabled'),
    Input('date-select', 'value'),
)
def update_fields(date_sel):
    if date_sel:
        return True, True
    return False, False


if __name__ == '__main__':
    app.run(debug=True)