from dash import dcc, html
import dash_bootstrap_components as dbc

layout = html.Div(children=[
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
                    html.Ul(className="darkerlishadowdown", children=[
                        html.Li(children=[
                            html.A(href="/energy", children=[
                               html.Img(src="../assets/enerji-takibi.png", className="nav-icon"),
                                html.Span(className="nav-text", children="Energy")
                            ])
                        ])
                    ]),
                ]),
            ]),
        ]),
    ]),

    dbc.Container(children=[
        dbc.Row(
            [
                dbc.Col(
                    html.A(
                        html.Div(
                            "Tutarlama",
                            style={
                                "height": "200px",
                                "border-radius": "10px",
                                "justify-content": "center",
                                "align-items": "center",
                                "display": "flex",
                                "background-color":"white"
                            },
                        ),
                        href="/value", style={"text-decoration": "none", "color":"#2149b4", "font-size":"24px"},
                    ),className="mt-2 col-lg-3 col-md-7 col-sm-12",
                ),
                dbc.Col(
                    html.A(
                        html.Div(
                            "Üretim Raporları",
                            style={
                                "height": "200px",
                                "border-radius": "10px",
                                "justify-content": "center",
                                "align-items": "center",
                                "display": "flex",
                                "background-color":"white"
                            },
                        ),
                        href="/uretimrapor", style={"text-decoration": "none", "color":"#2149b4", "font-size":"24px"},
                    ),className="mt-2 col-lg-3 col-md-7 col-sm-12 link-hover",
                ),
                dbc.Col(
                    html.A(
                        html.Div(
                            "Canlı Takip",
                            style={
                                "height": "200px",
                                "border-radius": "10px",
                                "justify-content": "center",
                                "align-items": "center",
                                "display": "flex",
                                "background-color":"white"
                            },
                        ),
                        href="/liveprd", style={"text-decoration": "none", "color":"#2149b4", "font-size":"24px"},
                    ),className="mt-2 col-lg-3 col-md-7 col-sm-12 link-hover",
                ),
                dbc.Col(
                    html.A(
                        html.Div(
                            "TV Monitor",
                            style={
                                "height": "200px",
                                "border-radius": "10px",
                                "justify-content": "center",
                                "align-items": "center",
                                "display": "flex",
                                "background-color":"white"
                            },
                        ),
                        href="/tvmonitor", style={"text-decoration": "none", "color":"#2149b4", "font-size":"24px"},
                    ),className="mt-2 col-lg-3 col-md-7 col-sm-12 link-hover",
                ),
                dbc.Col(
                    html.A(
                        html.Div(
                            "Energy ",
                            style={
                                "height": "200px",
                                "border-radius": "10px",
                                "justify-content": "center",
                                "align-items": "center",
                                "display": "flex",
                                "background-color":"white"
                            },
                        ),
                        href="/energy", style={"text-decoration": "none", "color":"#2149b4", "font-size":"24px"},
                    ),className="mt-2 col-lg-3 col-md-7 col-sm-12 link-hover",
                ),
            ],style={"justify-content":"center", "align-items":"center", "display":"flex",}
        )
    ],)
])
