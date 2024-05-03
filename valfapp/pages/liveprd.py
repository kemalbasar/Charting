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
                    html.Img(src='./assets/valfsan-logo.png', className="logo")
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
                    html.Li(className="darkerlishadow",children=[
                        html.A(href="/value", children=[
                            html.Img(src="../assets/tutarlama-icon.PNG", className="nav-icon"),
                            html.Span(className="nav-text", children="Tutarlama")
                        ])
                    ]),
                    html.Li(className="darkerli",children=[
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
                    html.Li(className="darkerli",children=[
                        html.A(href="/tvmonitor", children=[
                            html.Img(src="../assets/tvmonitor-ıcon.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Tv Monitor")
                        ])
                    ]),
                    html.Li(className="darkerli",children=[
                        html.A(href="/kapasite", children=[
                            html.Img(src="../assets/kapaste-removebg-preview.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Kapasite")
                        ])
                    ]),
                    html.Li(className="darkerli",children=[
                        html.A(href="/energy", children=[
                            html.Img(src="../assets/enerji-removebg-preview.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Energy")
                        ])
                    ]),
                    html.Li(className="darkerli",children=[
                        html.A(href="/prdenergy", children=[
                            html.Img(src="../assets/prof-enrgy-removebg-preview.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Prod Energy")
                        ])
                    ]),
                    html.Li(className="darkerli",children=[
                        html.A(href="/kameraayiklama", children=[
                            html.Img(src="../assets/k-ayıklama-removebg-preview.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Kam. Ayıklama")
                        ])
                    ]),
                    html.Label("Valfsan Engineers © 2024 ", id="signature-label", className="float-left signature-label-sb")
                ]),
            ]),
        ]),
    ]),
    html.Div(
        style={
            "justify-content": "center",
            "align-items": "center",
            "height": "100vh",
        },
        children=[
            dbc.Container(
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                html.A(
                                    html.Div(
                                        "Talaşlı İmalat",
                                        style={
                                            "height": "200px",
                                            "border-radius": "10px",
                                            "justify-content": "center",
                                            "align-items": "center",
                                            "display": "flex",
                                            "background-color": "white"
                                        },
                                    ),
                                    href="/livecnc", style={"text-decoration": "none", "color": "#2149b4", "font-size": "24px"},
                                ), className="mt-2 col-lg-3 col-md-7 col-sm-12 link-hover",
                            ),
                            dbc.Col(
                                html.A(
                                    html.Div(
                                        "Preshane",
                                        style={
                                            "height": "200px",
                                            "border-radius": "10px",
                                            "justify-content": "center",
                                            "align-items": "center",
                                            "display": "flex",
                                            "background-color": "white"
                                        },
                                    ),
                                    href="liveprd/livepres", style={"text-decoration": "none", "color": "#2149b4", "font-size": "24px"},
                                ), className="mt-2 col-lg-3 col-md-7 col-sm-12 link-hover",
                            ),
                            dbc.Col(
                                html.A(
                                    html.Div(
                                        "Tablo",
                                        style={
                                            "height": "200px",
                                            "border-radius": "10px",
                                            "justify-content": "center",
                                            "align-items": "center",
                                            "display": "flex",
                                            "background-color": "white"
                                        },
                                    ),
                                    href="/yonlendirmepagee", style={"text-decoration": "none", "color": "#2149b4", "font-size": "24px"},
                                ), className="mt-2 col-lg-3 col-md-7 col-sm-12 link-hover",
                            ),
                        ], style={"justify-content": "center", "align-items": "center", }
                    )
                ])
        ]
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


