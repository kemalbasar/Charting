from dash import html
from valfapp.layouts import nav_bar
import dash_bootstrap_components as dbc

layout = html.Div(children=[

    nav_bar,

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
