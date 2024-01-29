from dash import dcc, html
import dash_bootstrap_components as dbc


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
                    ])
                ])
            ])
        ]),
    ]),

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

