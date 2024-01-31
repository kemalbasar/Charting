from dash import dcc, html
import dash_bootstrap_components as dbc

from valfapp.layouts import nav_bar

layout = [
    nav_bar,

    dbc.Row([
        dbc.Col(
            # dcc.Link("Geri", href='/', className='btn btn-info br-1 mt-2',
            #          style={"border-radius":"10px",'margin-left':50})
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
                                'border':'1px solid red',
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
                                        'position':'absolute',
                                        "border-radius":"20px"
                                    },
                                    children=""
                                ),
                                html.Img(
                                     src='/assets/Taslama.png',
                                )
                            ],
                        ),
                        href='/taslamatv', style={"width":"310px"},
                    )
                ]
            ),
            className="mt-2 col-lg-3 col-md-6 col-sm-12",
        ),
        dbc.Col(
            html.Div(
                className="row justify-content-center",
                children=[
                    dcc.Link(
                        html.Div(
                            className="mt-2 justify-content-center",
                            style={
                                'border':'1px solid red',
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
                                        'position':'absolute',
                                        "border-radius":"20px"
                                    },
                                    children=""
                                ),
                                html.Img(
                                     src='/assets/Montaj.png',
                                )
                            ],
                        ),
                        href='/montajtv', style={"width":"310px"},
                    )
                ]
            ),
            className="mt-2 col-lg-3 col-md-6 col-sm-12",
        ),
        dbc.Col(
            html.Div(
                className="row justify-content-center",
                children=[
                    dcc.Link(
                        html.Div(
                            className="mt-2 justify-content-center",
                            style={
                                'border':'1px solid red',
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
                                        'position':'absolute',
                                        "border-radius":"20px"
                                    },
                                    children=""
                                ),
                                html.Img(
                                    src='/assets/Yislem.png',
                                )
                            ],
                        ),
                        href='/yislemtv', style={"width":"310px"},
                    )
                ]
            ),
            className="mt-2 col-lg-3 col-md-6 col-sm-12",
        ),
        dbc.Col(
            html.Div(
                className="row justify-content-center",
                children=[
                    dcc.Link(
                        html.Div(
                            className="mt-2 justify-content-center",
                            style={
                                'border':'1px solid red',
                                'width': '300px',
                                'height': '200px',
                                'borderRadius': '200px',
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
                                        "border-radius":"200px"
                                    },
                                    children=""
                                ),
                                html.Img(
                                     src='/assets/Cnc-torna.png',
                                )
                            ],
                        ),
                        href='/cnctotv', style={"width":"310px"},
                    )
                ]
            ),
            className="mt-2 col-lg-3 col-md-6 col-sm-12",
        ),
    ], className="mt-5")
]

