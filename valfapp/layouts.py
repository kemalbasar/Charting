import dash_bootstrap_components as dbc
from dash import dcc, html
from valfapp.functions.functions_val import total_value
total_value_with_separator = "{:,.0f}".format(int(total_value))



layout_27 = dbc.Container([
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
        dbc.Col(html.Div(children=[html.Div(["Current Value2", html.Br(), total_value],
                                            style={"fontSize": 24, "text-align": "center",
                                                   "color": "white",
                                                   "font-weight": "bold",
                                                   "background-color": "firebrick",
                                                   'margin-top': 50,
                                                   'margin-right': 80, "height": 70,
                                                   "width": 300}),
                                   html.Div(children=[
                                       html.Button(id='rawmat', n_clicks=0,
                                                   children='Raw Material'),
                                       html.Button(id='prod', n_clicks=0,
                                                   children='Product'),
                                       html.Button(id='halfprod', n_clicks=0,
                                                   children='Half Product')],
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

layout_12 = dbc.Container([
    dbc.Row(html.Div(html.Button(id='year', value="2022", children='Click me'),hidden=True)),
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
                #"background-color": "#FFEBCD",
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
                                        style={"margin-left":180,"color": '#cd5c5c' , "background-color": "#FFEBCD"}),
                            html.Button(id='prod', n_clicks=0, children='Product',
                                        style={"margin-left":0,"color": '#cd5c5c' , "background-color": "#FFEBCD"}),
                            html.Button(id='halfprod', n_clicks=0, children='Half Product',
                                        style={"margin-left":0,"color": '#cd5c5c' , "background-color": "#FFEBCD"}),
                            html.Br(),
                            dcc.Graph(id="linechart", figure={}, style={"margin-top": 1}),
            ]),
            style={"height": 100},
            width=7
        )
    ],style={"margin-top": 15}), # Missing bracket was added here
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


