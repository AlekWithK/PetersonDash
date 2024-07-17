# Packages
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd

# Local
from utils.func import importData
from utils.lang.en import *
from utils.design.layout import *
from utils.const import *

# Data import and preprocess 
df = importData('src/assets/data/PETERSON_FINAL.parquet')
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
        dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=BRAND_LOGO, className="navbar-img")),
                                dbc.Col(dbc.NavbarBrand(headerTitle, className="navbar-title")),
                            ],
                            align="center",
                            className="navbar-row",
                        ),
                        href=PETERSON_HREF,
                        style={"textDecoration": "none"},
                    ),
                ],
            className='navbar-container'
            ),
        color="grey",
        dark=True,
        className="navbar drop-shadow"
        ),
        # Begin body
        dbc.Row(align='top', children=[
            dbc.Col(className='col1', children=[
            dbc.Container(className='option-container', children=[
                dbc.Card(className='option-card drop-shadow', children=[
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
                    dbc.Row(dbc.ModalTitle('Map Tile', className='option-modal')),
                    dcc.Dropdown(
                        options=[{'label': 'Open Street Map', 'value': 'open-street-map'}],
                        value='open-street-map',
                        placeholder='Open Street Map',
                        clearable=False,
                        id='map-select',
                        className='option-select',
                        style={'border-top': 'none', 
                            'border-radius': '0px',
                            'border-right': 'none'}
                    ),
                ])
            ]),
            dbc.Container(className='option-container', children=[
                dbc.Card(className='option-card drop-shadow', children=[
                    dbc.Row(dbc.ModalTitle('Graph Options', className='option-modal')),
                    dbc.Checklist(className='station-toggle', id='station-toggle',
                                  options=[{"label": "Show Stations", "value": 1}],
                                  value=[0],
                                  switch=True)
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

@callback(
    Output('spatial-plot', 'figure'),
    Input('param-select', 'value'),
    Input('date-select', 'value'),
    Input('map-select', 'value')
)
def update_graph(param, date, mapTile):
    dfg = df.copy()
    dfg.datetime = pd.to_datetime(dfg.datetime)

    # For now, sample data if not already sampled by a date to speed things up
    if not date:
        dfg = dfg.sample(n=10000)
    else:
        dfg = df.copy()
        dfg = dfg[dfg.datetime.dt.date.astype(str) == date]
    
    fig = px.scatter_mapbox(dfg, lat='lat', lon='lon', hover_name=dfg.datetime.dt.date, hover_data={param, 'file', 'dataset'}, color=param,
                            zoom=3, color_continuous_scale=px.colors.sequential.Viridis, opacity=0.75)

    fig = fig.update_layout(mapbox_style=mapTile,
                            margin={"r": 0, "t": 0, "l": 0, "b": 0},
                            mapbox={'center': {'lat': 37.81, 'lon': -121.99},
                                    'zoom': 9},
                            autosize=True,
                            paper_bgcolor='#999',
                            coloraxis=dict(
                                colorbar=dict(thickness=20, len=0.60, x=0.01, y=0.32,
                                              title=f'{PARAM_NAME_UNIT_DICT[param][0]} ({PARAM_NAME_UNIT_DICT[param][1]})',
                                              outlinecolor='black', outlinewidth=1.5, title_side='bottom')),
                            font=dict(size=14, weight='bold'))


    return fig

if __name__ == '__main__':
    app.run(debug=True)