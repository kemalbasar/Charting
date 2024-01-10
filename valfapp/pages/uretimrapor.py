from dash import dcc, html
import dash_bootstrap_components as dbc

layout = [
    dbc.Row([
        dbc.Col(
            dcc.Link(
                "Geri",
                href='/',
                className='btn btn-info br-1 mt-2',
                style={"border-radius": "10px"}
            )
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(
                className="row justify-content-center",
                children=[
                    dcc.Link(
                        html.Div(
                            className="mt-2 justify-content-center",
                            style={
                                'border': '1px solid red',
                                'width': '300px',
                                'height': '200px',
                                'borderRadius': '10px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'background-color': 'lightgray',
                            },
                            children=[
                                html.Div(
                                    style={
                                        'font-size': '18px',
                                        'color': 'White',
                                        'position': 'absolute',
                                        "border-radius": "20px"
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
            className="mt-2 col-lg-6 col-md-6 col-sm-12",
        ),
        dbc.Col(
            html.Div(
                className="row justify-content-center",
                children=[
                    dcc.Link(
                        html.Div(
                            className="mt-2 justify-content-center",
                            style={
                                'border': '1px solid red',
                                'width': '300px',
                                'height': '200px',
                                'borderRadius': '10px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'background-color': 'lightgray',
                            },
                            children=[
                                html.Div(
                                    style={
                                        'font-size': '18px',
                                        'color': 'White',
                                        'position': 'absolute',
                                        "border-radius": "20px"
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
            className="mt-2 col-lg-6 col-md-6 col-sm-12",
        ),
    ])
]
