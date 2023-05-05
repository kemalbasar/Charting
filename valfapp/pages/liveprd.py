import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from valfapp.app import app
import dash_bootstrap_components as dbc

from valfapp.pages import livecnc, livepres

# Define the Dash app

# Define the layout for the main page
layout = html.Div(
    style={
        "display": "flex",
        "justify-content": "center",
        "align-items": "center",
        "height": "100vh",
    },
    children=[
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Link(
                            children=[
                                html.Div(
                                    [
                                        html.Img(
                                            src="/assets/cnc.jpg",
                                            style={
                                                "width": "100%",
                                                "height": "100%",
                                                "object-fit": "cover",
                                                "object-position": "center",
                                            },
                                        ),
                                        html.H1(
                                            "Talaşlı İmalat",
                                            style={
                                                "color": "white",
                                                "font-weight": "bold",
                                                "position": "absolute",
                                                "bottom": 0,
                                                "left": "50%",
                                                "transform": "translateX(-50%)",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "position": "relative",
                                        "width": "100%",
                                        "height": "480px",
                                        "text-align": "center",
                                    },
                                )
                            ],
                            href="/liveprd/livecnc",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dcc.Link(
                            children=[
                                html.Div(
                                    [
                                        html.Img(
                                            src="/assets/pres.png",
                                            style={
                                                "width": "100%",
                                                "height": "100%",
                                                "object-fit": "cover",
                                                "object-position": "center",
                                            },
                                        ),
                                        html.H1(
                                            "Preshane",
                                            style={
                                                "color": "white",
                                                "font-weight": "bold",
                                                "position": "absolute",
                                                "bottom": 0,
                                                "left": "50%",
                                                "transform": "translateX(-50%)",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "position": "relative",
                                        "width": "100%",
                                        "height": "480px",
                                        "text-align": "center",
                                    },
                                )
                            ],
                            href="/liveprd/livepres",
                        ),
                        width=6,
                    ),
                ],
                justify="center",
                style={"padding": 15},
            ),
            fluid=True,
        )
    ],
)




# Define the callbacks for routing
@app.callback(Output('page-content2', 'children'),
              Input('url', 'pathname'))
def display_page(pathname, liveprd=None):
    if pathname == '/liveprd/livecnc':
        return livecnc.layout
    elif pathname == '/liveprd/livepres':
        return livepres.layout
    else:
        return 404


