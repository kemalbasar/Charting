import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px  # (version 4.7.0 or higher)
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import pandas as pd
from functions import df_for_sunburst, scatter_plot, production_quantities, get_mean_prdqty, get_daily_qty, \
    generate_for_sparkline, working_machines, get_gann_data
import warnings
warnings.filterwarnings("ignore")
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', None)


def return_sparks(graph1="fig_prod", graph2="fig_scrap", margin_left=65):
    return html.Div(children=[dcc.Graph(id=graph1, figure={},
                                        style={'width': '22vh', 'height': '9vh', "margin-top": 70,
                                               "margin-left": margin_left}),
                              dcc.Graph(id=graph2, figure={},
                                        style={'width': '22vh', 'height': '9vh', "margin-top": 50,
                                               "margin-left": margin_left})])


def return_summary_data(data1=["Production Volume", get_daily_qty()],
                        data2=["Working Machine", working_machines[-1]],
                        margin_left=60):
    return html.Div(children=[html.Div(children=data1[1],
                                       style={"fontSize": 40, "color": "rgba(111, 213, 18, 0.6)",
                                              'text-align': 'center'}),
                              html.Div(children=data1[0],
                                       style={"fontSize": 25, "color": "white",
                                              'text-align': 'center'}),
                              html.Br(),
                              html.Div(children=data2[1],
                                       style={"fontSize": 40, "color": "rgba(221, 60, 0, 0.6)",
                                              'text-align': 'center'}),
                              html.Div(children=data2[0],
                                       style={"fontSize": 25, "color": "white",
                                              'text-align': 'center' }),
                              ],
                    style={"width": 300, "height": 250, 'color': px.colors.qualitative.Set3[1],
                           'fontSize': 25, 'text-align': 'left', "margin-top": 80, "margin-left": margin_left,
                            })


app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(
            html.H1("Daily Efficiency Dashboard", style={'text-align': 'center'}))
    ]),

    dbc.Row([
        dcc.Dropdown(id="slct_year",
                     options=[
                         {"label": "CNC", "value": "CNC"},
                         {"label": "CNC-To", "value": "CNCTO"},
                         {"label": "Taslama", "value": "TASLAMA"},
                     ],
                     multi=False,
                     value="CNC",
                     style={'width': "40%"}
                     )
    ]),

    dbc.Row([
        dbc.Col([
            html.H1("CNC Üretim Raporu", style={'text-align': 'center'})

        ], width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='sunburst', figure={}), width={"size": 2}),
        dbc.Col(
            [return_summary_data()],
            width={"offset": 4, "size": 1}, style={"margin-left": 30}),
        dbc.Col(
            [return_sparks(graph1="fig_prod", graph2="fig_working_machine",margin_left=115)], style={"margin-bot": 2},
            width={"size": 1}),
        dbc.Col(
            [return_summary_data(data1=["PPM", get_daily_qty(ppm=True)], data2=["Scrap", get_daily_qty(type='HURDA')],margin_left=120)],
            width={"size": 1}),
        dbc.Col(
            [return_sparks(graph1="fig_ppm", graph2="fig_scrap",margin_left=125)], style={"margin-bot": 2,'border-right':"7px rgb(218, 255, 160) dotted"}
            , width={"size": 2})

    ],style={"padding":"1px","size":10}),

    dbc.Row([
        dbc.Col([
            html.Div(id='output_container', children=[]),
            dcc.Graph(id='gann', figure={})
        ], width=12)
    ])

], fluid=True)


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='sunburst', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph_sunburst(option_slctd, report_day="2022-07-26", thrshlt=70):
    print(option_slctd)
    print(type(option_slctd))

    container = "The production field chosen by user was: " + option_slctd

    # Plotly Express
    df = df_for_sunburst(report_day=report_day)

    if df["OEE"]["PLANSIZDURUS"] > thrshlt:
        last_index = 9
    elif df["OEE"]["PLANSIZDURUS"] <= thrshlt:
        last_index = 17

    index_of_colors = [17, 9, 17, 4, 9, last_index, 19]
    index_of_colors = [px.colors.qualitative.Alphabet[index] for index in index_of_colors]
    # index_of_colors.insert(1, px.colors.qualitative.Light24[17])
    index_of_colors[3] = px.colors.qualitative.Set3[2]
    index_of_colors[1] = px.colors.qualitative.Light24[17]
    index_of_colors[4] = px.colors.qualitative.Light24[17]
    fig = px.sunburst(df, path=["OEE", "MACHINE", "OPR"], values="RATES", width=500, height=500,
                      color="RATES")

    fig.update_traces(textfont=dict(family=['Arial Black'], size=[20, 20, 20, 20, 20, 20, 35]),
                      marker_colors=index_of_colors)
    fig.update_layout(showlegend=False, paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                      title="Performance/MachineTime/OEE",
                      title_font_color=px.colors.qualitative.Set3[1], title_x=0.5, title_xanchor="center",
                      title_font_size=23)

    # fig.show(renderer='browser')

    return container, fig


# @app.callback(
#     [Output(component_id='bubble', component_property='figure')],
#     [Input(component_id='slct_year', component_property='value')]
# )
# def update_graph_bubble(report_day="2022-07-26"):
#     figs = scatter_plot()
#
#     #
#     # figs.update_traces(textfont=dict(family=['Arial Black']),
#     #                   marker_colors= px.colors.qualitative.Alphabet)
#     figs.update_xaxes(type="date", tickangle=90, fixedrange=True)
#     figs.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', font_color="white",
#                        title_font_family="Times New Roman",
#                        title_font_color="red")
#
#     return [figs]

@app.callback(
    [Output(component_id='gann', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_chart_gann(report_day="2022-07-26"):
    df = get_gann_data()
    print(df)
    print(df.isnull())
    figs = px.timeline(data_frame=df[["WORKSTART", "WORKEND", "WORKCENTER","CONFTYPE","STEXT"]], x_start="WORKSTART", x_end="WORKEND",
                y='WORKCENTER',color="CONFTYPE",color_discrete_map={"PROD":"green","BREAKDOWN":"red","SETUP":"blue"})

    #
    # figs.update_traces(textfont=dict(family=['Arial Black']),
    #                   marker_colors= px.colors.qualitative.Alphabet)
    figs.update_xaxes(type="date", tickangle=90, fixedrange=True)
    figs.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', font_color="white",
                       title_font_family="Times New Roman",
                       title_font_color="red")

    return [figs]


def get_spark_line(range=list(range(24)), data=generate_for_sparkline(type="HURDA")):
    return go.Figure(
        {
            "data": [
                {
                    "x": range,
                    "y": data,
                    "mode": "lines+markers",
                    "name": "item",
                    "line": {"color": "#f4d44d"},
                }
            ],
            "layout": {
                "uirevision": True,
                "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                "xaxis": dict(
                    showline=False,
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                ),
                "yaxis": dict(
                    showline=False,
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                ),
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
            },
        }
    )


@app.callback(
    [Output(component_id='fig_prod', component_property='figure'),
     Output(component_id='fig_scrap', component_property='figure'),
     Output(component_id='fig_working_machine', component_property='figure'),
     Output(component_id='fig_ppm', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_spark_line(report_day="2022-07-26"):
    fig_prod = get_spark_line(data=generate_for_sparkline())
    fig_scrap = get_spark_line()
    fig_working_machine = get_spark_line(data=working_machines)
    fig_ppm = get_spark_line(data=generate_for_sparkline(ppm=True))
    return [fig_prod, fig_scrap, fig_working_machine, fig_ppm]


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
