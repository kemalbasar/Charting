from dash import dcc, html
import dash_bootstrap_components as dbc
from valfapp.layouts import nav_bar

layout = [
    nav_bar,
    dbc.Row([
        dbc.Col(
            html.Div(
                className="row justify-content-center",
                children=[
                    dcc.Link(
                        html.Div(
                            className="justify-content-center",
                            style={
                                'border': '1px solid red',
                                'width': '300px',
                                'height': '200px',
                                'borderRadius': '10px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'backgroundColor': 'lightgray',
                            },
                            children=[
                                html.Div(
                                    style={
                                        'fontSize': '18px',
                                        'color': 'White',
                                        'position': 'absolute',
                                        "borderRadius": "20px"
                                    },
                                    children=""
                                ),
                                html.Img(
                                    src='/assets/M.Merkezi OEE Raporu.png',
                                )
                            ],
                        ),
                        href='/prod_eff',
                        style={"width": "310px"},
                    )
                ]
            ),
            className="mt-2 col-lg-6 col-md-6 col-sm-12 px-1", # Adjusted padding here
        ),
        dbc.Col(
            html.Div(
                className="row justify-content-center",
                children=[
                    dcc.Link(
                        html.Div(
                            className="justify-content-center",
                            style={
                                'border': '1px solid red',
                                'width': '300px',
                                'height': '200px',
                                'borderRadius': '10px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'backgroundColor': 'lightgray',
                            },
                            children=[
                                html.Div(
                                    style={
                                        'fontSize': '18px',
                                        'color': 'White',
                                        'position': 'absolute',
                                        "borderRadius": "20px"
                                    },
                                    children=""
                                ),
                                html.Img(
                                    src='/assets/İs Merkezi Raporu.png',
                                )
                            ],
                        ),
                        href='/wcreport',
                        style={"width": "310px"},
                    )
                ]
            ),
            className="g-0", # Adjusted padding here
        ),
    ]) # This removes gutter spacing between columns
]

