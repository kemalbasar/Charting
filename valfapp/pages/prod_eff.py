import json
import warnings
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px  # (version 4.7.0 or higher)
from dash import dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import scatter_plot, get_daily_qty, calculate_oeemetrics, \
    generate_for_sparkline, working_machinesf, get_gann_data, return_ind_fig
from run.agent import ag
from config import project_directory
from valfapp.app import cache, oee, app

summary_color = 'black'

wc_usage = ag.run_query("SELECT STAND FROM IASROU009 WHERE STAND != '*'")


def apply_nat_replacer(x):
    x = str(x)
    if x == 'NaT':
        x = 'nat_replaced'
    else:
        x = x
    return x


new_line = '\n'
warnings.filterwarnings("ignore")
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', None)

oeelist = oee()


def return_tops(graph1="fig_up1", margin_top=0, graph2="fig_up2", graph3="fig_up3"):
    return html.Div(children=[dcc.Graph(id=graph1, figure={}, style={"margin-top": margin_top})])


def return_sparks(graph1="fig_prod", graph2="fig_scrap", margin_left=0):
    return html.Div(children=[dcc.Graph(id=graph1, figure={},
                                        style={'width': '12vh', 'height': '9vh', "margin-top": 50,
                                               "margin-left": margin_left}),
                              dcc.Graph(id=graph2, figure={},
                                        style={'width': '12vh', 'height': '9vh', "margin-top": 40,
                                               "margin-left": margin_left})])


# refresh_store = dcc.Store(id='refresh-store',
#                           data={'refresh_count': 0, 'dropdown_value': 'default_value'})


layout = dbc.Container([
    dbc.Row(dcc.Link(
        children='Main Page',
        href='/',
        style={"color": "black", "font-weight": "bold"}

    )),
    dbc.Row([
        dbc.Col(
            html.H1("Daily Efficiency Dashboard", style={'text-align': 'center', "textfont": 'Arial Black'}))
    ]),

    dbc.Row([html.Div(id='output', children=''),
             dcc.Dropdown(id="costcenter",
                          options=[{"label": cc, "value": cc} for cc in ["CNC", "CNCTORNA",
                                                                         "TASLAMA", "MONTAJ",
                                                                         "PRESHANE1","PRESHANE2"]],
                          multi=False,
                          value='CNC',
                          style={"color": "green", "background-color": "DimGray", 'width': 200}
                          )
             ]),

    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(id='sunburst'), width={"size": 4}),
                dbc.Col([
                    dbc.Row(
                        html.H5("Production Summary",
                                style={"background-color": "darkolivegreen", "text-align": "center",
                                       "color": summary_color, "width": 855})
                    ),
                    dbc.Row([
                        dbc.Col(id="my-output1",
                                width={"size": 1},
                                style={"margin-left": 0, 'border-bottom': "1px rgb(218, 255, 160) inset",
                                       'border-left': "1px rgb(218, 255, 160) inset"}),
                        dbc.Col(
                            [return_sparks(graph1="fig_prod", graph2="fig_working_machine", margin_left=120)], style={
                                'border-bottom': "1px rgb(218, 255, 160) inset"},
                            width={"size": 1}),
                        dbc.Col(
                            id="my-output2",
                            width={"size": 1}, style={'border-bottom': "1px rgb(218, 255, 160) inset"}),
                        dbc.Col(
                            [return_sparks(graph1="fig_ppm", graph2="fig_scrap", margin_left=300)]
                            , width={"size": 1},
                            style={"border-right": "1px rgb(218, 255, 160) inset", "padding-right": 600,
                                   'border-bottom': "1px rgb(218, 255, 160) inset", })]
                    )
                ], style={}, width={"size": 8})]
            ),

            dbc.Row([
                dbc.Col([
                    html.Div(children=[html.H5("Production Schedule",
                                               style={"width": 1400, "height": 25, "text-align": "center",
                                                      "background-color": "darkolivegreen",
                                                      "color": summary_color}),
                                       dcc.Graph(id='gann', figure={}),
                                       html.H5("Breakdowns & Reasons",
                                               style={"width": 1400, "height": 25, "text-align": "center",
                                                      "background-color": "darkolivegreen",
                                                      "color": summary_color}),
                                       dcc.Graph(id='bubble', figure={}),
                                       html.H5("Scraps with Reasons",
                                               style={"width": 1400, "height": 25, "text-align": "center",
                                                      "background-color": "darkolivegreen",
                                                      "color": summary_color}),
                                       dcc.Graph(id='fig_scatscrap', figure={})
                                       ])
                ],

                    width=20)
            ])
        ], width={"size": 9}),
        dbc.Col([html.H5("Best Performances", style={"width": 380, "height": 25, "text-align": "center",
                                                     "background-color": "darkolivegreen",
                                                     "color": summary_color}),
                 html.Div(return_tops(), style={"width": 350, "height": 250}),
                 html.Div(return_tops(graph1="fig_up2"), style={"width": 250, "height": 250}),
                 html.Div(return_tops(graph1="fig_up3"), style={"width": 250, "height": 250}),
                 html.H5("Worst Performances", style={"width": 380, "height": 25, "text-align": "center",
                                                      "background-color": "red",
                                                      "color": summary_color, "margin-top": 160}),
                 html.Div(return_tops(graph1="fig_down1"), style={"width": 250, "height": 250}),
                 html.Div(return_tops(graph1="fig_down2"), style={"width": 250, "height": 250}),
                 html.Div(return_tops(graph1="fig_down3"), style={"width": 250, "height": 250})

                 ], style={"border-left": "1px rgb(218, 255, 160) inset", "border-top": "1px rgb(218, 255, 160) inset",
                           "padding-left": 70}, width=3)
    ])

], fluid=True)


@app.callback(
    [Output(component_id='my-output1', component_property='children'),
     Output(component_id='my-output2', component_property='children')],
    Input(component_id='costcenter', component_property='value')
)
def return_summary_data(option_slctd):
    df_working_machines = ag.run_query(project_directory + r"\Charting\queries\working_workcenter.txt")
    data1 = ["Production Volume", get_daily_qty(df=oeelist[2], costcenter=option_slctd)]
    data2 = ["Working Machines", working_machinesf(working_machines=df_working_machines, costcenter=option_slctd)[-1]]
    data3 = ["PPM", get_daily_qty(df=oeelist[2], costcenter=option_slctd, ppm=True)]
    data4 = ["Scrap", get_daily_qty(df=oeelist[2], costcenter=option_slctd, type='SCRAPQTY')]

    return [html.Div(children=[html.Div(children=data1[1],
                                        style={"fontSize": 30, "color": summary_color,
                                               'text-align': 'center'}),
                               html.Div(children=data1[0],
                                        style={"fontSize": 12, "color": summary_color,
                                               'text-align': 'center'}),
                               html.Br(),
                               html.Div(children=data2[1],
                                        style={"fontSize": 30, "color": summary_color,
                                               'text-align': 'center', "margin-top": 20}),
                               html.Div(children=data2[0],
                                        style={"fontSize": 12, "color": summary_color,
                                               'text-align': 'center'}),
                               ],
                     style={"width": 300, "height": 250, 'color': px.colors.qualitative.Set3[1],
                            'fontSize': 25, 'text-align': 'left', "margin-top": 65, "margin-left": 0
                            }),
            html.Div(children=[html.Div(children=data3[1],
                                        style={"fontSize": 30, "color": summary_color,
                                               'text-align': 'center'}),
                               html.Div(children=data3[0],
                                        style={"fontSize": 12, "color": summary_color,
                                               'text-align': 'center'}),
                               html.Br(),
                               html.Div(children=data4[1],
                                        style={"fontSize": 30, "color": summary_color,
                                               'text-align': 'center', "margin-top": 20}),
                               html.Div(children=data4[0],
                                        style={"fontSize": 12, "color": summary_color,
                                               'text-align': 'center'}),
                               ],
                     style={"width": 300, "height": 250, 'color': px.colors.qualitative.Set3[1],
                            'fontSize': 25, 'text-align': 'left', "margin-top": 65, "margin-left": 200
                            })]


# ------------------------------------------------------------------------------


# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='sunburst', component_property='figure')],
    [Input(component_id='costcenter', component_property='value')]
)
def update_graph_sunburst(option_slctd, report_day="2022-07-26"):
    df = oeelist[0][option_slctd]
    if int(df["OEE"][0][0:2]) > 38:
        fig = px.sunburst(df, path=["OEE", "MACHINE", "OPR"], values="RATES", width=425, height=425,
                          color="RATES", color_continuous_scale=px.colors.diverging.RdYlGn,
                          color_continuous_midpoint=50)
    else:
        fig = px.sunburst(df, path=["OEE", "MACHINE", "OPR"], values="RATES", width=425, height=425,
                  color="RATES", color_continuous_scale=px.colors.diverging.RdYlGn_r,
                  color_continuous_midpoint=50)

    fig.update_traces(hovertemplate='<b>Actual Rate is %{value} </b>')
    fig.update_layout(showlegend=False, paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                      title="Perf.-Avail.-OEE",
                      title_font_color=summary_color, title_x=0.5, title_xanchor="center",
                      title_font_size=18)

    # fig.show(renderer='browser')

    return [fig]


@app.callback(
    [Output(component_id='bubble', component_property='figure')],
    [Input(component_id='costcenter', component_property='value')]
)
def update_graph_bubble(option_slctd, report_day="2022-07-26"):
    df, category_order = scatter_plot(df=oeelist[2].loc[oeelist[2]["COSTCENTER"] == option_slctd])
    figs = px.histogram(df, x="WORKCENTER", y="FAILURETIME",
                      color="STEXT",
                      hover_data=["WORKCENTER"],
                      color_discrete_sequence=px.colors.qualitative.Alphabet,
                      width=1500, height=500, category_orders={"STEXT": category_order})

    # figs.update_traces(textfont=dict(family=['Arial Black']))
    figs.update_xaxes(type="category", tickangle=90, fixedrange=True)
    # figs.update_yaxes(categoryorder="total descending")
    figs.update_layout(xaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.2)'),
                       yaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.2)'),
                       paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='white', font_color=summary_color,
                       title_font_family="Times New Roman", title_font_color="red", width=1400, height=420,

                       )

    return [figs]


@app.callback(
    [Output(component_id='gann', component_property='figure')],
    [Input(component_id='costcenter', component_property='value')]
)
def update_chart_gann(option_slctd, report_day="2022-07-26", font_color=summary_color):
    df = oeelist[2].loc[oeelist[2]["COSTCENTER"] == option_slctd]
    df.sort_values(by="CONFTYPE", ascending=False, inplace=True)
    figs = px.timeline(data_frame=df[["WORKSTART", "WORKEND", "WORKCENTER", "CONFTYPE", "STEXT", "QTY"]],
                       x_start="WORKSTART",
                       x_end="WORKEND",
                       y='WORKCENTER', color="CONFTYPE",
                       color_discrete_map={"Uretim": "forestgreen", "Plansiz Durus": "red"
                           , "Ariza Durusu": "Brown", "Planli Durus": "Coral"
                           , "Kurulum": "Aqua"})

    #
    # figs.update_traces(textfont=dict(family=['Arial Black']),
    #                   marker_colors= px.colors.qualitative.Alphabet)
    figs.update_xaxes(type="date", tickangle=90, fixedrange=True)
    figs.update_yaxes(categoryorder="category ascending")
    figs.update_layout(barmode='overlay', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                       font_color=font_color,
                       title_font_family="Times New Roman", title_font_color="red", width=1300, height=420)

    return [figs]


def get_spark_line(data=pd.DataFrame(), range=list(range(24))):
    return go.Figure(

        {
            "data": [
                {
                    "x": range,
                    "y": data,
                    "mode": "lines+markers",
                    "name": "item",
                    "line": {"color": summary_color},
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
                "width": 225,
                "height": 65
            },
        }
    )


@app.callback(
    [Output(component_id='fig_prod', component_property='figure'),
     Output(component_id='fig_scrap', component_property='figure'),
     Output(component_id='fig_working_machine', component_property='figure'),
     Output(component_id='fig_ppm', component_property='figure')],
    [Input(component_id='costcenter', component_property='value')]
)
def update_spark_line(option_slctd, report_day="2022-07-26"):
    onemonth_prdqty = oeelist[6]
    df_working_machines = ag.run_query(project_directory + r"\Charting\queries\working_workcenter.txt")
    fig_prod = get_spark_line(data=generate_for_sparkline(data=onemonth_prdqty, proses=option_slctd))
    fig_scrap = get_spark_line(data=generate_for_sparkline(data=onemonth_prdqty, proses=option_slctd, type='HURDA'))
    fig_working_machine = get_spark_line(
        data=working_machinesf(working_machines=df_working_machines, costcenter=option_slctd))
    fig_ppm = get_spark_line(data=generate_for_sparkline(data=onemonth_prdqty, proses=option_slctd, ppm=True))
    return [fig_prod, fig_scrap, fig_working_machine, fig_ppm]


@app.callback(
    [Output(component_id='fig_up1', component_property='figure'),
     Output(component_id='fig_up2', component_property='figure'),
     Output(component_id='fig_up3', component_property='figure'),
     Output(component_id='fig_down1', component_property='figure'),
     Output(component_id='fig_down2', component_property='figure'),
     Output(component_id='fig_down3', component_property='figure')
     ],
    [Input(component_id='costcenter', component_property='value')]
)
def update_ind_fig(option_slctd, report_day="2022-07-26"):
    df = oeelist[1][oeelist[1]["COSTCENTER"] == option_slctd]
    fig_up1 = return_ind_fig(df_metrics=
                             df, costcenter=option_slctd)
    fig_up2 = return_ind_fig(df_metrics=
                             df, costcenter=option_slctd, order=1)
    fig_up3 = return_ind_fig(df_metrics=
                             df, costcenter=option_slctd, order=2)
    fig_down1 = return_ind_fig(df_metrics=df, costcenter=option_slctd, order=-1, colorof='red')
    fig_down2 = return_ind_fig(df_metrics=df, costcenter=option_slctd, order=-2, colorof='red')
    fig_down3 = return_ind_fig(df_metrics=df, costcenter=option_slctd, order=-3, colorof='red')
    return [fig_up1, fig_up2, fig_up3, fig_down1, fig_down2, fig_down3]


@app.callback(
    [Output(component_id='fig_scatscrap', component_property='figure')],
    [Input(component_id='costcenter', component_property='value')]
)
def create_scatterplot_for_scrapqty(costcenter):
    df_scrap = ag.run_query(r"EXEC VLFPRDSCRAP")
    df_scrap = df_scrap[df_scrap["COSTCENTER"] == costcenter]
    cat_order_sumscrap = df_scrap.groupby("STEXT")["SCRAP"].sum().sort_values(ascending=False).index
    df_scrap["SCRAP"] = df_scrap["SCRAP"].astype("int")
    fig = px.histogram(data_frame=df_scrap.loc[df_scrap["COSTCENTER"] == costcenter],
                     x="WORKCENTER",
                     y="SCRAP",
                     color="STEXT",
                     hover_data=["MTEXTX"],
                     width=1500, height=500,
                     category_orders={"STEXT": cat_order_sumscrap})
    # fig.update_traces(textfont=dict(family=['Arial Black']))
    fig.update_xaxes(type="category", tickangle=90, fixedrange=True)
    # figs.update_yaxes(categoryorder="total descending")
    fig.update_layout(xaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.2)'),
                      yaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.2)'),
                      paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='white', font_color=summary_color,
                      title_font_family="Times New Roman", title_font_color="red", width=1400, height=420,

                      )
    return [fig]


# @app.callback(
# [Output('costcenter', 'value')],
# [Input('costcenter', 'value')])
# def update_dropdown(options):
# global refresh_count
# refresh_count += 1
# print(refresh_count)
# print(costcenters[refresh_count%3])
# new_value = costcenters[refresh_count%3]
#    return [new_value]


# @app.callback(Output('page-1-refresh-count', 'children'),
#               [Input('interval', 'n_intervals')])
# def update_page_1_refresh_count(n):
#     global refresh_count
#     refresh_count = n
#     return f"Refresh count: {refresh_count}"

# ------------------------------------------------------------------------------
