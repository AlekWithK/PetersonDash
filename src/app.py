# Packages
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Local
from utils.func import importData
from utils.lang.en import *
from utils.design.layout import defineLayout
from utils.const import *

#df = importData('src/assets/data/PETERSON_FINAL.parquet')

# App init
app = Dash(
    __name__,
    title = 'SF Bay Flowthrough',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Set application layout
app.layout = html.Div(children=[
    dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=BRAND_LOGO, className="navbar-img")),
                            dbc.Col(dbc.NavbarBrand("SF BAY PETERSON FLOWTHROUGH", class_name="navbar-title")),
                        ],
                        align="center",
                        class_name="navbar-row",
                    ),
                    href="https://www.usgs.gov",
                    style={"textDecoration": "none"},
                ),
            ]
        ),
    color="grey",
    dark=True,
    class_name="navbar"
    )
])


if __name__ == '__main__':
    app.run(debug=True)