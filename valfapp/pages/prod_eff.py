import warnings
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px  # (version 4.7.0 or higher)
import dash
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
from valfapp.functions_prd import calculate_oeemetrics, scatter_plot, get_daily_qty, \
    generate_for_sparkline, working_machinesf, get_gann_data
from valfapp.app import app
import time


new_line = '\n'
df_oee, df_metrics = calculate_oeemetrics()
warnings.filterwarnings("ignore")
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', None)


refresh_interval = 45  # seconds
start_time = time.time()
refresh_count = 0




def return_tops(graph1="fig_up1", margin_top=0, graph2="fig_up2", graph3="fig_up3"):
    return html.Div(children=[dcc.Graph(id=graph1, figure={}, style={"margin-top": margin_top})])


def return_sparks(graph1="fig_prod", graph2="fig_scrap", margin_left=0):
    return html.Div(children=[dcc.Graph(id=graph1, figure={},
                                        style={'width': '12vh', 'height': '9vh', "margin-top": 50,
                                               "margin-left": margin_left}),
                              dcc.Graph(id=graph2, figure={},
                                        style={'width': '12vh', 'height': '9vh', "margin-top": 75,
                                               "margin-left": margin_left})])


def return_ind_fig(df_metrics=df_metrics, costcenter='CNC', order=0, istext=0, colorof='green'):
    df_metrics = df_metrics[df_metrics["COSTCENTER"] == costcenter].sort_values(by="OEE", ascending=False)
    df_metrics.reset_index(inplace=True, drop=True)
    final_card = df_metrics.iloc[order]
    if order >= 0:
        if final_card['IDEALCYCLETIME'] == 0:
            text = None
        else:
            text = f"{final_card['WORKCENTER']} worked {int(final_card['AVAILABILITY'] * 100)}% of planned time." \
                   f"Operater <br> processed {int(final_card['QTY'] - (final_card['QTY'] * final_card['RUNTIME']) / final_card['IDEALCYCLETIME'])} " \
                   f"more material then avarge <br> with only {final_card['SCRAPQTY']} scrap"
    else:
        if final_card["QTY"] == 0:
            text = f"{final_card['WORKCENTER']} worked {int(final_card['AVAILABILITY'] * 100)}% of planned time." \
                   f"Operater <br> processed 0 less material <br> with  {final_card['SCRAPQTY']} scrap"
        else:
            if final_card['IDEALCYCLETIME'] == 0:
                text = None
            else:
                text = f"{final_card['WORKCENTER']} worked {int(final_card['AVAILABILITY'] * 100)}% of planned time." \
                       f"Operater <br> processed {int((final_card['RUNTIME'] * final_card['QTY']) / final_card['IDEALCYCLETIME'] - final_card['QTY'])} " \
                       f"less material then optimal <br> with  {final_card['SCRAPQTY']} scrap"

    if istext == 0:
        if colorof == 'green':
            colorof2 = 'yellow'
        else:
            colorof2 = colorof
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=final_card['OEE'] * 100,
            title={
                "text": f"{final_card['WORKCENTER']}</span><br><span style='font-size:1em;color:gray'>"},
            gauge={
                'axis': {'range': [None, 150]},
                'bar': {'color': colorof, "thickness": 1},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "black",
                'steps': [
                    {'range': [0, 33], 'color': 'white'},
                    {'range': [33, 80], 'color': 'white'},
                    {'range': [81, 100], 'color': 'white'},
                    {'range': [100, 150], 'color': 'white'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 6},
                    'thickness': 1,
                    'value': 80
                }
            },

            #       delta={'reference': 400, 'relative': True, "font": {"size": 40}},
            #        domain={'x': [0, 1], 'y': [0, 1]}
        ))

        annotation = {
            "height": 600,
            "width": 850,
            'xref': 'paper',  # we'll reference the paper which we draw plot
            'yref': 'paper',  # we'll reference the paper which we draw plot
            'x': 0.5,  # If we consider the x-axis as 100%, we will place it on the x-axis with how many %
            'y': -0.2,  # If we consider the y-axis as 100%, we will place it on the y-axis with how many %
            'text': text,
            # 'showarrow': True,
            # 'arrowhead': 3,
            'font': {'size': 13, 'color': colorof2}
        }

        fig.update_layout({
            "annotations": [annotation],
            # title={
            # # 'text': text,
            # # 'y': 1,
            # # 'x': 0.5,
            # # 'font': {'size': 17}
            # },
            "paper_bgcolor": "rgba(0,0,0,0)", "width": 350, "height": 350})

        return fig
    else:
        text = f"{final_card['WORKCENTER']} had been worked {final_card['AVAILABILITY']} % of its planned time without breakdown.\n" \
               f"Operater processed {final_card['QTY'] - (final_card['QTY'] * final_card['IDEALCYCLETIME']) / final_card['RUNTIME']} " \
               f"more material then avarge with only scrap {final_card['SCRAPQTY']} " \
               f"{final_card['WORKCENTER']}"
        return text

# refresh_store = dcc.Store(id='refresh-store',
#                           data={'refresh_count': 0, 'dropdown_value': 'default_value'})

costcenters = ["CNC", "CNCTORNA", "TASLAMA"]
costcenter_value = "CNC"

layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    ),
    dbc.Container([

    dbc.Row([
        dbc.Col(
            html.H1("Daily Efficiency Dashboard", style={'text-align': 'center', "textfont": 'Arial Black'}))
    ]),

    dbc.Row([
        dcc.Dropdown(id="costcenter",
                     options=[{"label": cc, "value": cc} for cc in costcenters],
                     multi=False,
                     value="costcenterval",
                     style={"color":px.colors.qualitative.Dark2[7] ,
                            "background-color": px.colors.qualitative.Set1[5],
                            "text-align": "center",'width': 250,'height':15,'font-size':40}
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
                                       "color": px.colors.qualitative.Set1[5], "width": 855})
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
                                                      "color": px.colors.qualitative.Set1[5]}),
                                       dcc.Graph(id='gann', figure={}),
                                       html.H5("Breakdowns & Reasons",
                                               style={"width": 1400, "height": 25, "text-align": "center",
                                                      "background-color": "darkolivegreen",
                                                      "color": px.colors.qualitative.Set1[5]}),
                                       dcc.Graph(id='bubble', figure={})
                                       ])
                ],

                    width=20)
            ])
        ], width={"size": 9}),
        dbc.Col([html.H5("Best Performances", style={"width": 380, "height": 25, "text-align": "center",
                                                     "background-color": "darkolivegreen",
                                                     "color": px.colors.qualitative.Set1[5]}),
                 html.Div(return_tops(), style={"width": 350, "height": 250}),
                 html.Div(return_tops(graph1="fig_up2"), style={"width": 250, "height": 250}),
                 html.Div(return_tops(graph1="fig_up3"), style={"width": 250, "height": 250}),
                 html.H5("Worst Performances", style={"width": 380, "height": 25, "text-align": "center",
                                                      "background-color": "red",
                                                      "color": px.colors.qualitative.Set1[5], "margin-top": 160}),
                 html.Div(return_tops(graph1="fig_down1"), style={"width": 250, "height": 250}),
                 html.Div(return_tops(graph1="fig_down2"), style={"width": 250, "height": 250}),
                 html.Div(return_tops(graph1="fig_down3"), style={"width": 250, "height": 250})

                 ], style={"border-left": "1px rgb(218, 255, 160) inset", "border-top": "1px rgb(218, 255, 160) inset",
                           "padding-left": 70}, width=3)
    ],style= {"margin-top":80})

], fluid=True)
])


@app.callback(
    [Output(component_id='my-output1', component_property='children'),
     Output(component_id='my-output2', component_property='children')],
    Input(component_id='costcenter', component_property='value')
)
def return_summary_data(option_slctd):
    data1 = ["Production Volume", get_daily_qty(costcenter=option_slctd)]
    data2 = ["Working Machines", working_machinesf(costcenter=option_slctd)[-1]]
    data3 = ["PPM", get_daily_qty(costcenter=option_slctd, ppm=True)]
    data4 = ["Scrap", get_daily_qty(costcenter=option_slctd, type='SCRAPQTY')]

    return [html.Div(children=[html.Div(children=data1[1],
                                        style={"fontSize": 40, "color": px.colors.qualitative.Set1[5],
                                               'text-align': 'center'}),
                               html.Div(children=data1[0],
                                        style={"fontSize": 12, "color": px.colors.qualitative.Set1[5],
                                               'text-align': 'center'}),
                               html.Br(),
                               html.Div(children=data2[1],
                                        style={"fontSize": 40, "color": px.colors.qualitative.Set1[5],
                                               'text-align': 'center', "margin-top": 20}),
                               html.Div(children=data2[0],
                                        style={"fontSize": 12, "color": px.colors.qualitative.Set1[5],
                                               'text-align': 'center'}),
                               ],
                     style={"width": 300, "height": 250, 'color': px.colors.qualitative.Set3[1],
                            'fontSize': 25, 'text-align': 'left', "margin-top": 65, "margin-left": 0
                            }),
            html.Div(children=[html.Div(children=data3[1],
                                        style={"fontSize": 40, "color": px.colors.qualitative.Set1[5],
                                               'text-align': 'center'}),
                               html.Div(children=data3[0],
                                        style={"fontSize": 12, "color": px.colors.qualitative.Set1[5],
                                               'text-align': 'center'}),
                               html.Br(),
                               html.Div(children=data4[1],
                                        style={"fontSize": 40, "color": px.colors.qualitative.Set1[5],
                                               'text-align': 'center', "margin-top": 20}),
                               html.Div(children=data4[0],
                                        style={"fontSize": 12, "color": px.colors.qualitative.Set1[5],
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
    # Plotly Express
    df = df_oee[option_slctd]
    # df.MACHINE = df.MACHINE.astype(str) + '%'
#    list_color = px.colors.diverging.RdYlGn
#    if df["OEE"][0] < 0.5: list_color.reverse()


    if df["OEE"][0] < 0 :
        fig = px.sunburst(df, path=["OEE", "MACHINE", "OPR"], values="RATES", width=425, height=425,
                          color="RATES", color_continuous_scale=px.colors.diverging.Temps, color_continuous_midpoint=50)
    else:
        fig = px.sunburst(df, path=["OEE", "MACHINE", "OPR"], values="RATES", width=425, height=425,
                          color="RATES", color_continuous_scale=px.colors.diverging.RdYlGn, color_continuous_midpoint=50)

    fig.update_traces(hovertemplate='<b>Actual Rate is %{value} </b>')
    fig.update_layout(showlegend=False, paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                      title="Perf.-Avail.-OEE",
                      title_font_color=px.colors.qualitative.Set1[5], title_x=0.5, title_xanchor="center",
                      title_font_size=30)

    # fig.show(renderer='browser')

    return [fig]


@app.callback(
    [Output(component_id='bubble', component_property='figure')],
    [Input(component_id='costcenter', component_property='value')]
)
def update_graph_bubble(option_slctd, report_day="2022-07-26"):
    figs = scatter_plot(costcenter=option_slctd)

    figs.update_traces(textfont=dict(family=['Arial Black']))
    figs.update_xaxes(type="date", tickangle=90, fixedrange=True)
    figs.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', font_color="white",
                       title_font_family="Times New Roman", title_font_color="red", width=1400, height=420
                       )

    return [figs]


@app.callback(
    [Output(component_id='gann', component_property='figure')],
    [Input(component_id='costcenter', component_property='value')]
)
def update_chart_gann(option_slctd, report_day="2022-07-26"):
    df = get_gann_data(costcenter=option_slctd)

    figs = px.timeline(data_frame=df[["WORKSTART", "WORKEND", "WORKCENTER", "CONFTYPE", "STEXT", "QTY"]],
                       x_start="WORKSTART",
                       x_end="WORKEND",
                       y='WORKCENTER', color="CONFTYPE",
                       color_discrete_map={"PROD": "rgba(0, 255, 38, 0.3)", "BREAKDOWN": "red",
                                           "SETUP": px.colors.qualitative.Set1[5]})

    #
    # figs.update_traces(textfont=dict(family=['Arial Black']),
    #                   marker_colors= px.colors.qualitative.Alphabet)
    figs.update_xaxes(type="date", tickangle=90, fixedrange=True)
    figs.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', font_color="white",
                       title_font_family="Times New Roman", title_font_color="red", width=1300, height=420)

    return [figs]


def get_spark_line(range=list(range(24)), data=generate_for_sparkline(proses="CNC", type="HURDA")):
    return go.Figure(
        {
            "data": [
                {
                    "x": range,
                    "y": data,
                    "mode": "lines+markers",
                    "name": "item",
                    "line": {"color": px.colors.qualitative.Set1[5]},
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
    fig_prod = get_spark_line(data=generate_for_sparkline(proses=option_slctd))
    fig_scrap = get_spark_line()
    fig_working_machine = get_spark_line(data=working_machinesf(costcenter=option_slctd))
    fig_ppm = get_spark_line(data=generate_for_sparkline(proses=option_slctd, ppm=True))
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
    fig_up1 = return_ind_fig(costcenter=option_slctd, istext=0)
    fig_up2 = return_ind_fig(costcenter=option_slctd, order=1, istext=0)
    fig_up3 = return_ind_fig(costcenter=option_slctd, order=2, istext=0)
    fig_down1 = return_ind_fig(costcenter=option_slctd, order=-1, istext=0, colorof='red')
    fig_down2 = return_ind_fig(costcenter=option_slctd, order=-2, istext=0, colorof='red')
    fig_down3 = return_ind_fig(costcenter=option_slctd, order=-3, istext=0, colorof='red')
    return [fig_up1, fig_up2, fig_up3, fig_down1, fig_down2, fig_down3]

@app.callback(
    [Output('costcenter', 'value')],
    [Input('costcenter', 'value')])
def update_dropdown(options):
    global refresh_count
    refresh_count += 1
    print(refresh_count)
    print(costcenters[refresh_count%3])
    new_value = costcenters[refresh_count%3]
    return [new_value]


# @app.callback(Output('page-1-refresh-count', 'children'),
#               [Input('interval', 'n_intervals')])
# def update_page_1_refresh_count(n):
#     global refresh_count
#     refresh_count = n
#     return f"Refresh count: {refresh_count}"

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
