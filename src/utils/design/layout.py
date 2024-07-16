from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from utils.lang.en import *
from utils.const import *

navbar = dbc.Navbar(
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
    )

optionsContainer = dbc.Container(className='option-container', children=[
        dbc.Card(className='option-card drop-shadow', children=[
            dbc.Row(dbc.ModalTitle('Parameter', className='option-modal')),
            dcc.Dropdown(
                options=['Chlorophyll', 'Salinity', 'Water Temperature'],
                placeholder='Select...',
                id='param-select',
                className='option-select',
            )
        ])
    ])

    