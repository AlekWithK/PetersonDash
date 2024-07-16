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

#df = importData('src/assets/data/PETERSON_FINAL.parquet')

# App init
app = Dash(
    __name__,
    title = 'SF Bay Flowthrough',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Set application layout
app.layout = dmc.MantineProvider(
    html.Div(children=[
    navbar,
    dbc.Row(align='top', children=[
        optionsContainer,
        dbc.Container(className='map-container', fluid=True, children=[
            dbc.Card(className='map-card drop-shadow', children=[
                dbc.Row(dbc.ModalTitle('Transect Visualization', className='map-modal')),
                dcc.Graph(id='spatial-plot')
            ])
        ])
    ])
])
)


if __name__ == '__main__':
    app.run(debug=True)