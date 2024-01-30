import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from valfapp.app import app
import dash_bootstrap_components as dbc

from valfapp.pages import livecnc, livepres

# Define the Dash app

# Define the layout for the main page
layout = [
    html.Nav(className="main-menu side-bar", children=[
        dbc.Container([
            html.Div(className="logo-div resim-container", children=[
                html.A(className="logo", href="/", children=[
                    html.Img(src='/assets/valf-logo.gif', className="logo")
                ])
            ]),
            html.Div(className="settings"),
            html.Div(id="style-1", className="scrollbar", children=[
                html.Ul(children=[
                    html.Li(children=[
                        html.A(href="/", children=[
                            html.Img(src="../assets/home.png", className="nav-icon"),
                            html.Span(className="nav-text nav-text-2", children="MAIN")
                        ])
                    ]),
                    html.Li(className="darkerlishadow", children=[
                        html.A(href="/value", children=[
                            html.Img(src="../assets/tutarlama-icon.PNG", className="nav-icon"),
                            html.Span(className="nav-text", children="Tutarlama")
                        ])
                    ]),
                    html.Li(className="darkerli", children=[
                        html.A(href="/uretimrapor", children=[
                            html.Img(src="../assets/uretim-raporlari-icon.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Üretim Raporları")
                        ])
                    ]),
                    html.Li(className="darkerli", children=[
                        html.A(href="/liveprd", children=[
                            html.Img(src="../assets/uretim-takip-icon.PNG", className="nav-icon"),
                            html.Span(className="nav-text", children="Üretim Takip")
                        ])
                    ]),
                    html.Li(className="darkerli", children=[
                        html.A(href="/tvmonitor", children=[
                            html.Img(src="../assets/tvmonitor-ıcon.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Tv Monitor")
                        ])
                    ]),
                    html.Ul(className="darkerlishadowdown", children=[
                        html.Li(children=[
                            html.A(href="/energy", children=[
                                html.Img(src="../assets/enerji-takibi.png", className="nav-icon"),
                                html.Span(className="nav-text", children="Energy")
                            ])
                        ])
                    ])
                ])
            ])
        ]),
    ])
    ,
    html.Div(
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

]


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


