import warnings
from datetime import date, timedelta, datetime
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px  # (version 4.7.0 or higher)
from dash import dcc, html, Input, Output, State, callback_context, \
    no_update, exceptions  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc

from valfapp.configuration import layout_color
from valfapp.functions.functions_prd import scatter_plot, get_daily_qty, \
    generate_for_sparkline, working_machinesf, indicator_with_color
from run.agent import ag
from valfapp.app import app, prdconf, return_piechart
from valfapp.layouts import nav_bar
from valfapp.pages.date_class import update_date, update_date_output
from config import kb

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


def return_tops(graph1="fig_up1", margin_top=0, graph2="fig_up2", graph3="fig_up3"):
    return html.Div(children=[dcc.Graph(id=graph1, figure={}, style={"margin-top": margin_top})])


def return_sparks(graph1="fig_prod", graph2="fig_scrap", margin_left=0):
    return html.Div(children=[dcc.Graph(id=graph1, figure={},
                                        style={'width': '4vh', 'height': '2vh', "margin-top": 50,
                                               "margin-left": margin_left}),
                              dcc.Graph(id=graph2, figure={},
                                        style={'width': '4vh', 'height': '2vh', "margin-top": 100,
                                               "margin-left": margin_left})])



# Main Layout
layout = dbc.Container([
    dcc.Store(id='oeelist0',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), (date.today() - timedelta(days=kb-1)).isoformat(), "day"))[0]),
    dcc.Store(id='oeelist1',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), (date.today() - timedelta(days=kb-1)).isoformat(), "day"))[1]),
    dcc.Store(id='oeelist2',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), (date.today() - timedelta(days=kb-1)).isoformat(), "day"))[2]),
    dcc.Store(id='oeelist6',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), (date.today() - timedelta(days=kb-1)).isoformat(), "day"))[6]),
    dcc.Store(id='device-info-store'),
        nav_bar,

        dbc.Row([
            dbc.Col([
                dcc.DatePickerSingle(
                    id='date-picker2',
                    className="dash-date-picker mt-2",
                    date=(date.today() - timedelta(days=kb)),
                    persistence=True,
                    persistence_type='memory'
                ),
                dbc.Button("Day", id="btn-day2", n_clicks=0, color="primary", className='day-button',
                           style={}),
                dbc.Button("Week", id="btn-week2", n_clicks=0, color="primary", className='week-button',
                           style={}),
                dbc.Button("Month", id="btn-month2", n_clicks=0, color="primary", className='month-button',
                           style={}),
                dbc.Button("Year", id="btn-year2", n_clicks=0, color="primary", className='year-button',
                           style={}),
                dcc.Store(
                    id="work-dates",
                    storage_type="memory",
                    data={"workstart": (date.today() - timedelta(days=kb)).isoformat(),
                          "workend": (date.today() - timedelta(days=kb-1)).isoformat(),
                          "interval": "day"},
                ),
                dcc.Location(id='location3', refresh=True),
                html.Div(id='output', children=''),
                html.Div(
                    dcc.Dropdown(
                        id="costcenter",
                        className="dropdown-style",
                        options=[{"label": cc, "value": cc} for cc in
                                 ["CNC", "CNCTORNA", "TASLAMA", "MONTAJ", "PRESHANE1", "PRESHANE2"]],
                        multi=False,
                        value='CNC',
                    ), style={"position": "relative", "left": 475, "bottom": 50}
                ),
            ], style={"border": "3px dashed #2149b5", "height": "70px", "border-radius": "20px",
                      "margin-top": "5rem"}, ),
        ]),

        html.Div(id='refresh3', style={'display': 'none'}),

        dcc.Store(id='store-costcenter', storage_type='memory', data='CNC'),
        dbc.Row(style={"text-align": "center", "justify-content": "center"}, children=[
            dbc.Col(children=[
                dbc.Row(html.Div([dcc.Graph(id='sunburst')], style={"margin-left": 300})),
                dbc.Row([
                    dbc.Col(children=[
                        dbc.Row(html.H5("Üretim Özeti", style={
                            "background-color": "#2149b4",
                            "text-align": "center",
                            "color": "white",
                        })),
                        dbc.Row([
                            dbc.Col(id="my-output1", width={"size": 1}, style={"margin-left": 0}),
                            dbc.Col([return_sparks(graph1="fig_prod", graph2="fig_working_machine", margin_left=180)],
                                    width={"size": 1}),
                            dbc.Col(id="my-output2", width={"size": 1}, style={"margin-left": 80}),
                            dbc.Col([return_sparks(graph1="fig_ppm", graph2="fig_scrap", margin_left=385)],
                                    width={"size": 1},
                                    style={"padding-right": 300})
                        ], style={"margin-left": 80})
                    ], style={}, width={"size": 12})
                ]),
                dbc.Row([
                    dbc.Col(children=[
                        html.Div(children=[
                            html.H5("Üretim Planı", style={
                                "height": 25,
                                "text-align": "center",
                                "background-color": "#2149b4",
                                "color": "white",
                                "margin-top": "30px"
                            }),
                            dcc.Graph(id='gann', figure={},
                                      style={"position": "relative", "right": "75px", "top": "10px"}),
                            html.H5("Arızalar ve Nedenler", style={
                                "height": 25,
                                "text-align": "center",
                                "background-color": "#2149b4",
                                "color": "white",
                                "margin-top": "50px"
                            }),
                            dcc.Graph(id='bubble', figure={},
                                      style={"position": "relative", "right": "75px", "top": "10px"}),
                            html.H5("Hurda ve Nedenleri", style={
                                "height": 25,
                                "text-align": "center",
                                "background-color": "#2149b4",
                                "color": "white",
                                "margin-top": "50px"
                            }),
                            dcc.Graph(id='fig_scatscrap', figure={},
                                      style={"position": "relative", "right": "75px", "top": "30px"})
                        ])
                    ], width=20)
                ])
            ], width={"size": 9}),

            dbc.Row([
                dbc.Col(children=[
                    html.H5("En İyi Performanslar", style={
                        "width": 400,
                        "height": 25,
                        "text-align": "center",
                        "background-color": "#2149b4",
                        "color": "white"
                    }),
                    html.Div(return_tops(), style={"margin-left": 35, "width": 350, "height": 250}),
                    html.Div(return_tops(graph1="fig_up2"), style={"margin-left": 35, "width": 250, "height": 250}),
                    html.Div(return_tops(graph1="fig_up3"), style={"margin-left": 35, "width": 250, "height": 250})
                ], width=4, style={
                    "border-right": "1px rgb(218, 255, 160) inset",
                    "border-left": "1px rgb(218, 255, 160) inset",
                    "border-top": "1px rgb(218, 255, 160) inset"
                }),
                dbc.Col(children=[
                    html.H5("En Kötü Performanslar", style={
                        "width": 400,
                        "height": 25,
                        "text-align": "center",
                        "background-color": "red",
                        "color": "white"
                    }),
                    html.Div(return_tops(graph1="fig_down1"), style={"margin-left": 35, "width": 250, "height": 250}),
                    html.Div(return_tops(graph1="fig_down2"), style={"margin-left": 35, "width": 250, "height": 250}),
                    html.Div(return_tops(graph1="fig_down3"), style={"margin-left": 35, "width": 250, "height": 250})
                ], width=4, style={
                    "border-right": "1px rgb(218, 255, 160) inset",
                    "border-left": "1px rgb(218, 255, 160) inset",
                    "border-top": "1px rgb(218, 255, 160) inset",
                    "margin-left": 80
                })
            ], style={"justify-content": "center", "text-align": "center", "margin-top": "120px"})
        ])

    ],style={"justify-content": "center", "align-items": "center"})



@app.callback(Output('store-costcenter', 'data'),
              Input('costcenter', 'value'))
def update_store(value):
    return value


@app.callback(Output('costcenter', 'value'),
              [Input('store-costcenter', 'modified_timestamp')],
              [State('store-costcenter', 'data')])
def update_dropdown(ts, stored_data):
    if ts is None:
        # if no data was stored yet, it initializes the dropdown to its default value
        raise exceptions.PreventUpdate
    return stored_data \
 \
 \
################################################################################################
################################ DATE BUTTONS START  ############################################
################################################################################################

@app.callback(
    [Output('work-dates', 'data'),
     Output('refresh3', 'children'),
     Output(component_id='oeelist0', component_property='data'),
     Output(component_id='oeelist1', component_property='data'),
     Output(component_id='oeelist2', component_property='data'),
     Output(component_id='oeelist6', component_property='data')],
    [Input('btn-day2', 'n_clicks'),
     Input('date-picker2', 'date'),
     Input('btn-week2', 'n_clicks'),
     Input('btn-month2', 'n_clicks'),
     Input('btn-year2', 'n_clicks')]
)
def update_work_dates(n1, date_picker, n2, n3, n4):
    stored_date = date_picker
    if n1 or date_picker or n2 or n3 or n4:
        data = update_date('2', date_picker, callback_context)
        print(f"params= {data}")
        if data != {}:
            oeelist = prdconf(params=(data["workstart"], data["workend"], data["interval"]))
            (oeelist[0], oeelist[1], oeelist[2], oeelist[6],)
            a = update_date_output(n1, date_picker, n2, n3, n4, data)
            return (a[0], 0) + (oeelist[0], oeelist[1], oeelist[2], oeelist[6],)
        else:
            return no_update
    else:
        return no_update


@app.callback(
    Output('location3', 'href'),
    Input('refresh3', 'children')
)
def page_refresh3(n3):
    if n3:
        return "/prodeff"
    return no_update


################################################################################################
################################ DATE BUTTONS END  ############################################
################################################################################################

@app.callback(
    [Output(component_id='my-output1', component_property='children'),
     Output(component_id='my-output2', component_property='children')],
    [Input(component_id='costcenter', component_property='value'),
     Input(component_id='work-dates', component_property='data'),
     Input(component_id='oeelist6', component_property='data')]
)
def return_summary_data(option_slctd, dates, oeelist6):
    oeelist6 = pd.read_json(oeelist6, orient='split')
    df_working_machines = ag.run_query(query=r"EXEC VLFWORKINGWORKCENTERS @WORKSTART=?, @WORKEND=?"
                                       , params=(dates["workstart"], dates["workend"]))
    data1 = ["Production Volume", get_daily_qty(df=oeelist6, costcenter=option_slctd)]
    data2 = ["Working Machines", working_machinesf(working_machines=df_working_machines, costcenter=option_slctd)[-1]]
    data3 = ["PPM", get_daily_qty(df=oeelist6, costcenter=option_slctd, ppm=True)]
    data4 = ["Scrap", get_daily_qty(df=oeelist6, costcenter=option_slctd, type='HURDA')]

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
    [Input(component_id='costcenter', component_property='value'),
     Input(component_id='oeelist0', component_property='data')]
)
def update_graph_sunburst(option_slctd, oeelist0):
    return [return_piechart(option_slctd, oeelist0)]


@app.callback(
    [Output(component_id='bubble', component_property='figure')],
    [Input(component_id='costcenter', component_property='value'),
     Input(component_id='oeelist2', component_property='data'),
     Input('device-info-store', 'data')]
)
def update_graph_bubble(option_slctd, oeelist2, dev_type):
    graphwidth = 1100
    oeelist2 = pd.read_json(oeelist2, orient='split')
    df, category_order = scatter_plot(df=oeelist2.loc[oeelist2["COSTCENTER"] == option_slctd])

    figs = px.histogram(df, x="WORKCENTER", y="FAILURETIME",
                        color="STEXT",
                        hover_data=["WORKCENTER"],
                        color_discrete_sequence=px.colors.qualitative.Alphabet,
                        width=1500, height=500, category_orders={"STEXT": category_order})
    # figs.update_traces(textfont=dict(family=['Arial Black']))
    figs.update_xaxes(type="category", tickangle=90, fixedrange=True, categoryorder='total ascending')
    # figs.update_yaxes(categoryorder="total descending")
    figs.update_layout(xaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.2)'),
                       yaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.2)'),
                       paper_bgcolor=layout_color, plot_bgcolor=layout_color, font_color=summary_color,
                       title_font_family="Times New Roman", title_font_color="red", width=graphwidth, height=420,
                       legend=dict(
                           bgcolor='lightgray',  # Background color of the legend
                           bordercolor='gray',  # Border color of the legend
                           borderwidth=1  # Border width of the legend
                       ),
                       )

    return [figs]


@app.callback(
    [Output(component_id='gann', component_property='figure')],
    [Input(component_id='costcenter', component_property='value'),
     Input(component_id='oeelist2', component_property='data')]
)
def update_chart_gann(option_slctd, oeelist2):
    graphwidth = 1100
    oeelist2 = pd.read_json(oeelist2, orient='split')
    df = oeelist2.loc[oeelist2["COSTCENTER"] == option_slctd]
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
    figs.update_layout(barmode='overlay', paper_bgcolor=layout_color, plot_bgcolor='rgba(0, 0, 0, 0)',
                       font_color=summary_color,
                       title_font_family="Times New Roman", title_font_color="red", width=graphwidth, height=420,
                       )
    figs.update_layout(legend=dict(
        bgcolor='lightgray',  # Background color of the legend
        bordercolor='gray',  # Border color of the legend
        borderwidth=1  # Border width of the legend
    ))

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
                "paper_bgcolor": layout_color,
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
    [Input(component_id='costcenter', component_property='value'),
     Input(component_id='work-dates', component_property='data'),
     Input(component_id='oeelist6', component_property='data')]
)
def update_spark_line(option_slctd, dates, oeelist6):
    onemonth_prdqty = pd.read_json(oeelist6, orient='split')
    df_working_machines = ag.run_query(query=r"EXEC VLFWORKINGWORKCENTERS @WORKSTART=?, @WORKEND=?"
                                       , params=(dates["workstart"], dates["workend"]))
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
    [Input(component_id='costcenter', component_property='value'),
     Input(component_id='oeelist1', component_property='data')]
)
def update_ind_fig(option_slctd, oeelist1):
    df = pd.read_json(oeelist1, orient='split')
    df = df[df["COSTCENTER"] == option_slctd]
    fig_up1 = indicator_with_color(df_metrics=df)
    fig_up2 = indicator_with_color(df_metrics=df, order=1)
    fig_up3 = indicator_with_color(df_metrics=df, order=2)
    fig_down1 = indicator_with_color(df_metrics=df, order=-1, colorof='red')
    fig_down2 = indicator_with_color(df_metrics=df, order=-2, colorof='red')
    fig_down3 = indicator_with_color(df_metrics=df, order=-3, colorof='red')
    return [fig_up1, fig_up2, fig_up3, fig_down1, fig_down2, fig_down3]


@app.callback(
    [Output(component_id='fig_scatscrap', component_property='figure')],
    [Input(component_id='costcenter', component_property='value'),
     Input(component_id='work-dates', component_property='data')]
)
def create_scatterplot_for_scrapqty(costcenter, dates):

    graphwidth = 1100
    now = datetime.now()
    df_scrap = ag.run_query(query=r"EXEC VLFPRDSCRAPWITHPARAMS @WORKSTART=?, @WORKEND=?"
                            , params=(dates["workstart"], dates["workend"]))
    now = datetime.now()
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
                      paper_bgcolor=layout_color, plot_bgcolor=layout_color, font_color=summary_color,
                      title_font_family="Times New Roman", title_font_color="red", width=graphwidth, height=420,
                      legend=dict(
                          bgcolor='lightgray',  # Background color of the legend
                          bordercolor='gray',  # Border color of the legend
                          borderwidth=1  # Border width of the legend
                      )
                      )
    return [fig]








