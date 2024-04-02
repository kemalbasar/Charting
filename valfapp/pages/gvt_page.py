import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from valfapp.layouts import nav_bar
import plotly.express as px
from run.agent import ag
from datetime import date, timedelta, datetime
from config import kb
from valfapp.app import app

# df = px.data.gapminder().query("continent=='Oceania'")
# fig = px.line(df, x="year", y="lifeExp", color='country')


work_dates_data = (date.today() - timedelta(days=kb)).isoformat()

layout = [dbc.Button(id="asdf"),
          dcc.Store(id='work-dateees'),

          html.Div([
              html.Div(
                  className="container-fluid mt-5 grafik-div",
                  children=[
                      dbc.Row([
                          dbc.Col(html.H3("GENEL VERİMLİLİK TABLOSU", className="text-center"))
                      ]),
                      dbc.Row(
                          justify="center",
                          align="center",
                          children=[
                              dbc.Col(
                                  dbc.Card(
                                      [
                                          dbc.CardHeader(
                                              html.Div(
                                                  className="row text-center text-light",
                                                  children=[
                                                      dbc.Col(html.H3("Genel Tezgah Verimliliği"),
                                                              className="bg-primary col-lg-7 ic-yazilar"),
                                                      dbc.Col([
                                                          html.H3("%85,44"),
                                                          html.P("Hedef %80")
                                                      ], className="bg-success col-lg-5 ic-yazilar-2 p-2")
                                                  ]
                                              )
                                          ),
                                          dbc.CardBody(
                                              dcc.Graph(id='fig_tezgah')
                                          ),
                                      ],
                                      className="grafik",
                                  ),
                                  className="col-lg-5 col-md-6 col-sm-12",
                              ),
                              dbc.Col(
                                  dbc.Card(
                                      [
                                          dbc.CardHeader(
                                              html.Div(
                                                  className="row text-center text-light",
                                                  children=[
                                                      dbc.Col(html.H3("Genel Personel Verimliliği"),
                                                              className="bg-primary col-lg-7 ic-yazilar"),
                                                      dbc.Col([
                                                          html.H3("%88,27"),
                                                          html.P("Hedef %90")
                                                      ], className="bg-danger col-lg-5 ic-yazilar-2 p-2")
                                                  ]
                                              )
                                          ),
                                          dbc.CardBody(
                                              dcc.Graph(id='fig_personal')
                                          ),
                                      ],
                                      className="grafik",
                                  ),
                                  className="col-lg-5 col-md-6 col-sm-12",
                              ),
                              dbc.Col(
                                  dbc.Card(
                                      [
                                          dbc.CardHeader(
                                              html.Div(
                                                  className="row text-center text-light",
                                                  children=[
                                                      dbc.Col(html.H3("Genel OEE Verimliliği"),
                                                              className="bg-primary col-lg-7 ic-yazilar"),
                                                      dbc.Col([
                                                          html.H3("%70,47"),
                                                          html.P("Hedef %65")
                                                      ], className="bg-success col-lg-5 ic-yazilar-2 p-2")
                                                  ]
                                              )
                                          ),
                                          dbc.CardBody(
                                              dcc.Graph(id='fig_oee')
                                          ),
                                      ],
                                      className="grafik",
                                  ),
                                  className="col-lg-5 col-md-6 col-sm-12",
                              ),
                              dbc.Col(
                                  dbc.Card(
                                      [
                                          dbc.CardHeader(
                                              html.Div(
                                                  className="row text-center text-light",
                                                  children=[
                                                      dbc.Col(html.H3("Genel Kapasite Verimliliği"),
                                                              className="bg-primary col-lg-7 ic-yazilar"),
                                                      dbc.Col([
                                                          html.H3("%69,91"),
                                                          html.P("Hedef %80")
                                                      ], className="bg-primary col-lg-5 ic-yazilar-2 p-2")
                                                  ]
                                              )
                                          ),
                                          dbc.CardBody(
                                              dcc.Graph(id='fig_kapasite')
                                          ),
                                      ],
                                      className="grafik",
                                  ),
                                  className="col-lg-5 col-md-6 col-sm-12",
                              ),
                          ]
                      ),
                      dbc.Row(
                          children=[
                              dbc.Col(
                                  html.Div(
                                      className="col-lg-3 col-md-6 col-sm-12 me-5 mt-5",
                                      children=[
                                          html.Div(
                                              style={"background-color": "#ffffff"},
                                              children=[
                                                  html.Div(
                                                      className="justify-content-center align-content-center gvt-div-1",
                                                      style={"height": "50px"},
                                                      children=[
                                                          html.P("Tezgah Çalışma Verimliliği",
                                                                 className="d-flex gvt-div-yazi"),
                                                          html.P("%85,44", className="text-end"),
                                                      ],
                                                  )
                                              ],
                                          ),
                                          html.Div(
                                              style={"background-color": "#e0e0e0"},
                                              children=[
                                                  html.Div(
                                                      className="justify-content-center align-content-center p-1 gvt-div-2",
                                                      style={"height": "50px"},
                                                      children=[
                                                          html.P("Planlı Duruş(Kurulum Setup)",
                                                                 className="d-flex gvt-div-yazi"),
                                                          html.P("%2,10", className="text-end"),
                                                      ],
                                                  )
                                              ],
                                          ),
                                          html.Div(
                                              style={"background-color": "#f0f0f0"},
                                              children=[
                                                  html.Div(
                                                      className="justify-content-center align-content-center p-1 gvt-div-3",
                                                      style={"height": "50px"},
                                                      children=[
                                                          html.P("Kalite Onay", className="d-flex gvt-div-yazi"),
                                                          html.P("%0,88", className="text-end"),
                                                      ],
                                                  )
                                              ],
                                          ),
                                          html.Div(
                                              style={"background-color": "#e0e0e0"},
                                              children=[
                                                  html.Div(
                                                      className="justify-content-center align-content-center p-1 gvt-div-4",
                                                      style={"height": "50px"},
                                                      children=[
                                                          html.P("Plansız Duruş", className="d-flex gvt-div-yazi"),
                                                          html.P("%5,79", className="text-end"),
                                                      ],
                                                  )
                                              ],
                                          ),
                                          html.Div(
                                              style={"background-color": "#f0f0f0"},
                                              children=[
                                                  html.Div(
                                                      className="justify-content-center align-content-center p-1 gvt-div-5",
                                                      style={"height": "50px"},
                                                      children=[
                                                          html.P("Diğer", className="d-flex gvt-div-yazi"),
                                                          html.P("%5,79", className="text-end"),
                                                      ],
                                                  )
                                              ],
                                          ),
                                          html.Div(
                                              style={"background-color": "#e0e0e0"},
                                              children=[
                                                  html.Div(
                                                      className="justify-content-center align-content-center p-1 gvt-div-6",
                                                      style={"height": "50px"},
                                                      children=[
                                                          html.P("OPR Devamsızlığı", className="d-flex gvt-div-yazi"),
                                                          html.P("%2,78", className="text-end"),
                                                      ],
                                                  )
                                              ],
                                          ),
                                      ], style={"width": 300},
                                  ), className="col-lg-2 me-5 mt-3"
                              ),
                              dbc.Col(
                                  html.Div([
                                      html.Div(
                                          className="card col-lg-3 col-md-6 col-sm-12 me-3 mt-sm-4 justify-content-center align-items-center grafik-divler",
                                          children=[
                                              html.Div(className="card-body alt-divler", children=[
                                                  dcc.Graph(id='fig_planlı', style={"height": "280px"})
                                              ])
                                          ]),
                                      html.Div(
                                          className="card col-lg-3 col-md-6 col-sm-12 me-3 mt-sm-4 justify-content-center align-items-center grafik-divler",
                                          children=[
                                              html.Div(className="card-body alt-divler", children=[
                                                  dcc.Graph(id="fig_plansız", style={"height": "280px"})
                                              ])
                                          ]),
                                      html.Div(
                                          className="card col-lg-3 col-md-6 col-sm-12 mt-sm-4 justify-content-center align-items-center grafik-divler",
                                          children=[
                                              html.Div(className="card-body alt-divler", children=[
                                                  dcc.Graph(id='fig_kalite', style={"height": "280px"})
                                              ])
                                          ])
                                  ], className="row mt-lg-5 justify-content-center aligns-item-center d-flex")
                              )
                          ], style={"margin-left": "150px"},
                      ),
                  ],
              ),
          ])
          ]


@app.callback(
    [Output('fig_oee', 'figure'),
     Output('fig_personal', 'figure'),
     Output('fig_tezgah', 'figure')],
    Input('asdf', 'n_clicks')
)
def update_graph(n):
    work_date = datetime.fromisoformat(work_dates_data)
    day_of_week = work_date.weekday()
    days_until_saturday = (5 - day_of_week) % 7
    if days_until_saturday == 0:
        saturday_date = work_date
    else:
        saturday_date = work_date + timedelta(days=days_until_saturday)
    saturday_date_iso = saturday_date.date().isoformat()
    df = ag.run_query(r"SELECT * FROM VLFOEE WHERE PERIOD = 'week' AND COSTCENTER = 'CNC'")
    print('ko')
    print(df)
    print(saturday_date_iso)
    df = df[df['OEEDATE'] == saturday_date_iso]
    print('ko2')
    print(df)
    fig = px.line(df, x="OEEDATE", y="OEE")
    fig_personal = px.line(df, x="OEEDATE", y="PERFORMANCE")
    fig_tezgah = px.line(df, x="OEEDATE", y="AVAILABILITY")
    return fig, fig_personal, fig_tezgah

# Second Div
# html.Div(
#     className="container-fluid mt-5 grafik-div-2",
#     children=[
#         dbc.Row(
#             justify="center",
#             align="center",
#             children=[
#                 # First Column with Data
#                 dbc.Col(
#                     # Content of the first column...
#                     html.Div(
#                         className="col-lg-2 col-md-6 col-sm-12 me-5 mt-5",
#                         children=[
#                             html.Div(
#                                 style={"background-color": "#f0f0f0"},
#                                 children=[
#                                     html.Div(
#                                         className="justify-content-center align-content-center p-1",
#                                         style={"height": "50px"},
#                                         children=[
#                                             "Tezgah Çalışma Verimliliği",
#                                             html.P("%85,44", className="text-end"),
#                                         ],
#                                     )
#                                 ],
#                             ),
#                             html.Div(
#                                 style={"background-color": "#e0e0e0"},
#                                 children=[
#                                     html.Div(
#                                         className="justify-content-center align-content-center p-1",
#                                         style={"height": "50px"},
#                                         children=[
#                                             "Planlı Duruş(Kurulum Setup)",
#                                             html.P("%2,10", className="text-end"),
#                                         ],
#                                     )
#                                 ],
#                             ),
#                             html.Div(
#                                 style={"background-color": "#f0f0f0"},
#                                 children=[
#                                     html.Div(
#                                         className="justify-content-center align-content-center p-1",
#                                         style={"height": "50px"},
#                                         children=[
#                                             "Kalite Onay",
#                                             html.P("%0,88", className="text-end"),
#                                         ],
#                                     )
#                                 ],
#                             ),
#                             html.Div(
#                                 style={"background-color": "#e0e0e0"},
#                                 children=[
#                                     html.Div(
#                                         className="justify-content-center align-content-center p-1",
#                                         style={"height": "50px"},
#                                         children=[
#                                             "Plansız Duruş",
#                                             html.P("%5,79", className="text-end"),
#                                         ],
#                                     )
#                                 ],
#                             ),
#                             html.Div(
#                                 style={"background-color": "#f0f0f0"},
#                                 children=[
#                                     html.Div(
#                                         className="justify-content-center align-content-center p-1",
#                                         style={"height": "50px"},
#                                         children=[
#                                             "Diğer",
#                                             html.P("%5,79", className="text-end"),
#                                         ],
#                                     )
#                                 ],
#                             ),
#                             html.Div(
#                                 style={"background-color": "#e0e0e0"},
#                                 children=[
#                                     html.Div(
#                                         className="justify-content-center align-content-center p-1",
#                                         style={"height": "50px"},
#                                         children=[
#                                             "OPR Devamsızlığı",
#                                             html.P("%2,78", className="text-end"),
#                                         ],
#                                     )
#                                 ],
#                             ),
#                         ],
#                     )
#                 ),

#             ]
#         )
#     ]
# ),

# html.Div(
#     className="container-fluid mt-5 grafik-div-2",
#     children=[
#         dbc.Row(
#             justify="center",
#             align="center",
#             children=[
#                 # First Column with Data
#                 dbc.Col(
#                     # Content of the first column...
#                     html.Div([
#                         html.Div(className="card card col-lg-3 col-md-6 col-sm-12 me-5 grafik", children=[
#                             html.Div(className="card-body")
#                         ]),
#                         html.Div(className="card card col-lg-3 col-md-6 col-sm-12 me-5 grafik", children=[
#                             html.Div(className="card-body")
#                         ]),
#                         html.Div(className="card card col-lg-3 col-md-6 col-sm-12 me-5 grafik", children=[
#                             html.Div(className="card-body")
#                         ])
#                     ])
#                 ),
#                 # dbc.Col(...) for other columns
#             ]
#         )
#     ]
# )

