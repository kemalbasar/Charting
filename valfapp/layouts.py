import dash_bootstrap_components as dbc
import datetime as dt
import pandas as pd
from dash import dcc, html
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from config import project_directory
from run.agent import ag
from valfapp.app import return_piechart, prdconf
from valfapp.functions.functions_prd import indicator_for_tvs

cur_week = (dt.datetime.now() + relativedelta(months=-1)).strftime('%Y-%U').zfill(6)
try:
    value = int(
        ag.run_query(f"SELECT SUM(VALUE) AS TOTALVAL FROM VLFVALUATION WHERE VALDATE = '{cur_week}'")["TOTALVAL"][0])
except TypeError:
    value = int(1200000)

total_value_with_separator = format(value, ",")

today = datetime.today()

if today.weekday() == 6:
    kb = 2
elif today.weekday() == 0:
    kb = 3
else:
    kb = 1


###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### NAV BAR NAV BAR NAV VAR ###### ###### ###### ###
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######


nav_bar = html.Nav(className="main-menu side-bar", children=[
        dbc.Container([
            html.Div(
                className="logo-div resim-container",
                children=[
                    dbc.Row(
                        html.A(
                            className="logo",
                            href="/",
                            children=[html.Img(src='/assets/valf-logo.gif', className="logo")]
                        )
                    ),
                    dbc.Row(
                        html.H3("VALFSAN", style={"margin-top":15,"color": '#2149b4'})
                    )
                ]
            )
            ,
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
                            html.Img(src="../assets/kapasite-logo.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Kapasite")
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
    ])



###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### VALUATION LAYOUTS ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######

layout_27 = dbc.Container([
    dbc.Row(dcc.Link(
        children='Main Page',
        href='/',
        style={"height": 40, "color": "black", "font-weight": "bold"}

    )),
    dbc.Row(html.Button(id='year', value="2022", children='Click me')),
    dbc.Row([

        dbc.Col([html.Div(dcc.Graph(id="piec", figure={}, style={"margin-top": 20}))],
                style={"width": 300, "height": 500, "border-right": "6px black inset"}),

        dbc.Col(html.Div(children=[html.Div(["Current Value", html.Br(), total_value_with_separator],
                                            style={'margin-top': 50, 'margin-left': 100,
                                                   "fontSize": 24,
                                                   "text-align": "center", "color": "white",
                                                   "font-weight": "bold",
                                                   "background-color": "firebrick",
                                                   "height": 70,
                                                   "width": 300}),
                                   html.Br(),
                                   dcc.Graph(id="linechart", figure={},
                                             style={"margin-top": 1, 'margin-right': 520})],
                         style={"height": 100, "width": 250})),
        dbc.Col(html.Div(children=[html.Div(children=[
            html.Button(id='rawmat', n_clicks=0,
                        children='Raw Material'),
            html.Button(id='prod', n_clicks=0,
                        children='Product'),
            html.Button(id='halfprod', n_clicks=0,
                        children='Half Product'),
            html.Button(id='main', n_clicks=0, children='General',

                        style={"margin-left": 0, "color": '#cd5c5c',
                               "background-color": "#FFEBCD"}),
        ],
            style={"margin-top": 50,
                   "background-color": "burlywood"})
        ], style={}))],
        style={"background-color": "#FFEBCD", "width": 1900, "height": 500}),
    dbc.Row(
        [

            html.Div(children=["Div 1", html.Div(dcc.Graph(id="MAMÜL",
                                                           figure={}))],
                     style={"background-color": "#FFEBCD", "width": 944, "height": 600,
                            "margin-top": 9}),

            html.Div(children=["Div 2", html.Div(dcc.Graph(id="HAMMADDE",
                                                           figure={}))],
                     style={"background-color": "#FFEBCD", "width": 944, "height": 600,
                            "margin-left": 6,
                            "margin-top": 9})

        ]
    ),
    dbc.Row(
        [
            html.Div(children=["Div 1", html.Div(dcc.Graph(id="YARI MAMÜL",
                                                           figure={}))],
                     style={"background-color": "#FFEBCD", "width": 944,
                            "height": 600,
                            "margin-top": 1, }),
            html.Div(children=["Div 2", html.Div(dcc.Graph(id="YARDIMCI MALZEME",
                                                           figure={}))],
                     style={"background-color": "#FFEBCD", "width": 944,
                            "height": 600,
                            "margin-left": 6,
                            "margin-top": 1, })

        ], style={"margin-top": 15}
    )

], fluid=True
)

###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######


layout_12 = dbc.Container([
    nav_bar,

    dbc.Row(dcc.Link(
        children='Main Page',
        href='/',
        style={"height": 40, "color": "black", "font-weight": "bold"}

    )),
    dbc.Row(html.Div(html.Button(id='year', value="2022", children='Click me'), hidden=True)),
    dbc.Row(
        html.Div(
            ["Current Value", html.Br(), total_value_with_separator],
            style={
                'margin-top': 5,
                "padding": 50,
                "fontSize": 30,
                "text-align": "center",
                "color": '#cd5c5c',
                "font-weight": "bold",
                # "background-color": "#FFEBCD",
                "height": 120,
                "width": 300,
                "display": "flex",  # Enable flexbox
                "justify-content": "center",  # Center horizontally
                "align-items": "center"  # Center vertically
            }
        ),
        style={
            "display": "flex",
            "justify-content": "center"  # Center the div within the row
        }
    ),
    dbc.Row([
        dbc.Col([html.Div(dcc.Graph(id="piec", figure={}, style={"margin-top": 20}))], width=5),
        dbc.Col(
            html.Div(children=[
                html.Button(id='rawmat', n_clicks=0, children='Raw Material',
                            style={"margin-left": 180, "color": '#cd5c5c', "background-color": "#FFEBCD"}),
                html.Button(id='prod', n_clicks=0, children='Product',
                            style={"margin-left": 0, "color": '#cd5c5c', "background-color": "#FFEBCD"}),
                html.Button(id='halfprod', n_clicks=0, children='Half Product',
                            style={"margin-left": 0, "color": '#cd5c5c', "background-color": "#FFEBCD"}),
                html.Button(id='main', n_clicks=0, children='General',
                            style={"margin-left": 0, "color": '#cd5c5c', "background-color": "#FFEBCD"}),
                html.Br(),
                dcc.Graph(id="linechart", figure={}, style={"margin-top": 1}),
            ]),
            style={"height": 100},
            width=7
        )
    ], style={"margin-top": 15}),  # Missing bracket was added here
    dbc.Row([
        dbc.Col(children=[html.Div(dcc.Graph(id="MAMÜL", figure={}))],
                style={"background-color": "#FFEBCD", "margin-top": 9}, width=6),
        dbc.Col(children=[html.Div(dcc.Graph(id="HAMMADDE", figure={}))],
                style={"background-color": "#FFEBCD", "margin-top": 9}, width=6)
    ]),
    dbc.Row([
        dbc.Col(children=[html.Div(dcc.Graph(id="YARI MAMÜL", figure={}))],
                style={"background-color": "#FFEBCD"}, width=6),
        dbc.Col(children=[html.Div(dcc.Graph(id="YARDIMCI MALZEME", figure={}))],
                style={"background-color": "#FFEBCD"}, width=6)
    ])
], fluid=True)

###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### MAIN PAGE LAYOUTS ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######

layout_12_loginpage_v2 = layout = html.Div(children=[
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
                            "Enerji Ölçüm",
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
                dbc.Col(
                    html.A(
                        html.Div(
                            "Kapasite (Geliştiriliyor)",
                            style={
                                "height": "200px",
                                "border-radius": "10px",
                                "justify-content": "center",
                                "align-items": "center",
                                "display": "flex",
                                "background-color":"white"
                            },
                        ),
                        href="/kapasite", style={"text-decoration": "none", "color":"#2149b4", "font-size":"24px"},
                    ),className="mt-2 col-lg-3 col-md-7 col-sm-12 link-hover",
                ),
            ],style={"justify-content":"center", "align-items":"center", "display":"flex",}
        )
    ],)
])


layout_12_loginpage = dbc.Container([
    dbc.Row([
        dbc.Col(
            children=[
                html.Div(
                    html.Img(src='assets/valfsan_logo2.png', className="valfsan-logo"),
                )
            ],
            width={"size": 12}
        )
    ], 
    className="container-fluid",
    style={"background-color": "rgba(187, 187, 187, 0.289)"}),

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
                                    src='/assets/Tutarlama.png',
                                )
                            ],
                        ),
                        href='/value', style={"width": "310px"},
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
                                    src='/assets/Üretim Raporları.png',
                                )
                            ],
                        ),
                        href='/uretimrapor', style={"width": "310px"},
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
                                    src='/assets/Yislem.png',
                                )
                            ],
                        ),
                        href='/deneme', style={"width": "310px"},
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
                                'border': '1px solid red',
                                'width': '300px',
                                'height': '200px',
                                'borderRadius': '10px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'background-color': 'lightgray',
                                'background-image': '/assets/Taslama.png',
                            },
                            children=[
                                html.Div(
                                    style={
                                        'font-size': '18px',
                                        'color': 'White',
                                        "border-radius": "20px"
                                    },
                                    children=""
                                ),
                                html.Img(
                                    src='/assets/Üretim takip.png',
                                )
                            ],
                        ),
                        href='/liveprd', style={"width": "310px"},
                    )
                ]
            ),
            className="mt-2 col-lg-3 col-md-6 col-sm-12",
        ),
    ], className="mt-5"),

    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    className="row justify-content-center",
                    children=[
                        dcc.Link(
                            html.Div(
                                className="mt-2 justify-content-center",
                                style={
                                    # 'border': '1px solid red',
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
                                        src='/assets/TV-Monitor.png',
                                    )
                                ],
                            ),
                            href='/tvmonitor', style={"width": "310px"},
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
                                    # 'border': '1px solid red',
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
                                        src='/assets/enerji.png',
                                    )
                                ],
                            ),
                            href='/energy', style={"width": "310px"},
                        ),
                        dcc.Link(
                            html.Div(
                                className="mt-2 justify-content-center",
                                style={
                                    # 'border': '1px solid red',
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
                                        src='/assets/enerji.png',
                                    )
                                ],
                            ),
                            href='/energy', style={"width": "310px"},
                        )
                    ]
                ),
                className="mt-2 col-lg-3 col-md-6 col-sm-12",
            ),
        ], style={'justify-content': 'center'}, className='mt-5',
    ),
], style={"height": "100vh", "position": "relative"}, fluid=True)



###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######

layout_27_loginpage = dbc.Container([
    # dcc.Interval(
    #     id='interval-component',
    #     interval=1000000, # 5000 milliseconds = 5 seconds
    #     n_intervals=0
    # ),
    dbc.Row([html.H1("Valfsan Analytics",
                     style={"text-align": "center", 'color': 'LightSteelBlue', 'font-weight': 'bold',
                            'padding': 50,
                            "width": 1000, "height": 100})],
            className="justify-content-center"),
    dbc.Row([
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/tutarlama.link.png',
                                 style={"width": "600px", "height": "400px", "object-fit": "fit"}),
                        html.H1("Tutarlama ( Geliştirme Aşamasında )", style={
                            "position": "absolute",
                            "bottom": 8,
                            "right": 8,
                            'color': 'white',
                            'font-weight': 'bold',
                        })
                    ], style={"position": "relative", "display": "inline-block"})
                ],
                href='/pg1',
            ),
            width=4,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding": 14, 'margin-left': 50}
        ),
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/report.link.png',
                                 style={"width": "600px", "height": "400px", "object-fit": "fit"}),
                        html.H1("M.Merkezi OEE Raporu", style={
                            "position": "absolute",
                            "bottom": 8,
                            "right": 8,
                            'color': 'white',
                            'font-weight': 'bold',
                        })
                    ], style={"position": "relative", "display": "inline-block"})
                ],
                href='/prod_eff',
            ),
            width=5,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding-top": 13, 'margin-left': 43}

        ),
    ], style={'margin-left': 270, 'margin-top': 37, 'margin-bottom': '-45px'}),
    dbc.Row([
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/wc.link.png',
                                 style={"width": "600px", "height": "400px", "object-fit": "fit"}),
                        html.H1("İş Merkezi Raporu", style={
                            "position": "absolute",
                            "bottom": 0,
                            "right": 10,
                            'color': 'white',
                            'font-weight': 'bold',
                        })
                    ], style={"position": "relative", "display": "inline-block"})
                ],
                href='/wcreport',
            ),
            width=4,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding-top": 30},

        ),
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/live.link.png',
                                 style={"width": "600px", "height": "400px", "object-fit": "fit"}),
                        html.H1("Üretim Canlı Takip", style={
                            "position": "absolute",
                            "bottom": 0,
                            "right": 8,
                            'color': 'white',
                            'font-weight': 'bold',
                        })
                    ], style={"position": "absolute", "display": "inline-block"})
                ], href='/liveprd'),
            width=5,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding": 28, 'margin-left': 42, 'margin-top': 2}
        ),
    ], style={'margin-left': 322}),
    dcc.Link(
        children='dragtester',
        href='/dragtester',
    )
], fluid=True)


def sliding_indicator_container(livedata, selected_value, costcenter):
    """

    Parameters
    ----------
    livedata: data source of  indicator data
    selected_value: current page of indicator groups
    costcenter: coscenter ( can be another filter of data ) to show

    Returns
    -------
    div of indicators group of 4 with line.

    """
    df = pd.read_json(livedata, orient='split')
    df = df[df["COSTCENTER"] == costcenter].reset_index(drop=True)

    list_of_figs = []
    list_of_stationss = []
    for item in df.loc[df["COSTCENTER"] == costcenter]["WORKCENTER"].unique():
        list_of_stationss.append(item)
    for index, row in df.iterrows():
        if index < len(list_of_stationss):
            fig = indicator_for_tvs(row["STATUSR"], row["FULLNAME"], row["WORKCENTER"], row["DRAWNUM"],
                                    row["STEXT"], 0,size={"width": 310, "height": 500},rate=3/4)

            list_of_figs.append(fig)

        else:
            fig = {}
            style = {"display": "none"}

    lengthof = len(list_of_figs)
    x = lengthof % 6
    newlengthof = lengthof - x
    numofforths = newlengthof / 6
    counter = 0

    listofdivs = []
    for i in range(0, len(list_of_figs), 6):
        if counter != numofforths:
            listofdivs.append(html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=list_of_figs[i]), style={
                        'border': '2px solid red'}, width=3),
                    dbc.Col(html.Div(children=[dcc.Graph(figure=list_of_figs[i + 1])], style={
                        'border': '2px solid red'}), width=3),
                    dbc.Col(html.Div(children=[dcc.Graph(figure=list_of_figs[i + 2])], style={
                        'border': '2px solid red'}), width=3)
                ], className="g-0"),
                dbc.Row([
                    dbc.Col(html.Div(children=[dcc.Graph(figure=list_of_figs[i + 3])], style={
                        'border': '2px solid red'}), width=3),
                    dbc.Col(html.Div(children=[dcc.Graph(figure=list_of_figs[i + 4])], style={
                        'border': '2px solid red'}), width=3),
                    dbc.Col(html.Div(children=[dcc.Graph(figure=list_of_figs[i + 5])], style={
                        'border': '2px solid red'}), width=3),
                ], className="g-0")
            ]))
        else:
            if x == 0:
                continue
            else:
                print("here")
                listofdivs.append(html.Div([
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i])), width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 1] if x > 1 else {})), width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 2] if x > 2 else {})), width=3)
                    ], className="g-0"),
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 3] if x > 3 else {})), width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 4] if x > 4 else {})), width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 5] if x > 5 else {})), width=3)
                    ], className="g-0")
                ]))
        counter = counter + 1

    selected_value = selected_value % len(listofdivs)

    return listofdivs[selected_value]


def layout_for_tvs(costcenter='MONTAJ'):
    print(f"pie_of_yesterday_{costcenter.lower()}")
    return [
        dcc.Store(id=f'oeelist1w_tv_{costcenter.lower()}',
                  data=prdconf(((date.today() - timedelta(days=kb)).isoformat(),
                                date.today().isoformat(), "day"))[1]),
        dcc.Store(id=f'oeelist3w_tv_{costcenter.lower()}',
                  data=prdconf(((date.today() - timedelta(days=kb)).isoformat(),
                                date.today().isoformat(), "day"))[
                      3]),
        dcc.Store(id=f'oeelist0w_tv_{costcenter.lower()}',
                  data=prdconf(((date.today() - timedelta(days=kb)).isoformat(),
                                date.today().isoformat(), "day"))[
                      0]),
        dcc.Store(id=f'oeelist7w_tv_{costcenter.lower()}',
                  data=prdconf(((date.today() - timedelta(days=kb)).isoformat(),
                                date.today().isoformat(), "day"))[
                      7]),
            # First Column
            dbc.Row([
                dbc.Col([
                    html.Div(id=f"wc-output-container_{costcenter.lower()}", className= "row g-0"),
                    # Other components for this column
                ], width=8),

                # Second Column
                dbc.Col([
                    dbc.Row([
                        dcc.Graph(id=f"pie_of_yesterday_{costcenter.lower()}")
                    ], className="g-0"),
                    dbc.Row([
                        html.Button("Play", id="play", style={'width': '45px'}),
                        dcc.Slider(
                            min=0,
                            max=15,
                            step=1,
                            value=0,
                            id=f'wc-slider_{costcenter.lower()}',
                            className = 'slider'
                        ),
                        html.Div(
                            id=f'slider-output-container_{costcenter.lower()}',style={'width':500, 'display': 'inline-block'}),
                        dcc.Interval(id=f"animate_{costcenter.lower()}", interval=10000, disabled=False),
                        dcc.Interval(id="15min_update", interval=80000, disabled=False),
                        dcc.Store(id="list_of_stationss"),
                        dcc.Store(
                            id=f"livedata_{costcenter.lower()}",
                            data=ag.run_query(project_directory + r"\Charting\queries\liveprd.sql").to_json(
                                date_format='iso',
                                orient='split')
                        ),
                    ],className="g-0"),
                ], width=3),
        ],className="g-0")]


