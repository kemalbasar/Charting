import warnings
from datetime import date, timedelta, datetime

import dash_table
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px  # (version 4.7.0 or higher)
from dash import dcc, html, Input, Output, State, callback_context, \
    no_update, exceptions  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc

from valfapp.configuration import layout_color
from valfapp.functions.functions_prd import scatter_plot, get_daily_qty, \
    generate_for_sparkline, working_machinesf, indicator_with_color, legend_generater
from run.agent import ag
from valfapp.app import app, prdconf, return_piechart, workcenters
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


def return_tops(graph1="fig_up1_forreports", margin_top=0, graph2="fig_up2_forreports", graph3="fig_up3_forreports"):
    return html.Div(children=[dcc.Graph(id=graph1, figure={}, style={"margin-top": margin_top})])


def return_sparks(graph1="fig_prod_forreports", graph2="fig_scrap__forreports", margin_left=0):
    return html.Div(children=[dcc.Graph(id=graph1, figure={},
                                        style={'width': '4vh', 'height': '2vh', "margin-top": 50,
                                               "margin-left": margin_left}),
                              dcc.Graph(id=graph2, figure={},
                                        style={'width': '4vh', 'height': '2vh', "margin-top": 100,
                                               "margin-left": margin_left})])


# Main Layout
layout = dbc.Container([
    dcc.Store(id='oeeelist0',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[0]),
    dcc.Store(id='oeeelist1',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[1]),
    dcc.Store(id='oeeelist2',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[2]),
    dcc.Store(id='oeeelist3',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[3]),
    dcc.Store(id='oeeelist6',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[6]),
    dcc.Store(id='oeeelist7',
              data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[7]),

    dcc.Store(id='work-datees', data={"workstart": (date.today() - timedelta(days=kb)).isoformat(),
                                      'workend': date.today().isoformat()}),

    html.Div(id='refresh3_forreports', style={'display': 'none'}),
    html.H2("CNC Bölüm Raporu", style={
        "background-color": "#2149b4",
        "text-align": "center",
        "color": "white",
        "padding": "10px",
        "margin-bottom": "20px",
        "border-radius": "5px",
        "font-family": "Arial, sans-serif",
        "box-shadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)"
    }),
    dbc.Row(html.H5("Performans(( Kullanılabilirlik(( OEE", style={
                    "background-color": "#2149b4",
                    "text-align": "center",
                    "color": "white",
                })),
    dbc.Row(
        dbc.Col(html.Div(id='sunburst_forreports'),
                width=12, className="d-flex justify-content-center",)
    ,className = "g-0"),
    dbc.Row([
        dbc.Col(children=[
            dbc.Row(html.H5("Üretim Özeti", style={
                "background-color": "#2149b4",
                "text-align": "center",
                "color": "white",
            })),
            dbc.Row([
                dbc.Col([
                    dbc.Col(id="my-output_forreports1", width={"size": 2}, style={"margin-left": 0}),
                    dbc.Col([return_sparks(graph1="fig_prod_forreports", graph2="fig_working_machine_forreports",
                                           margin_left=0)],
                            width={"size": 2}),
                    dbc.Col(id="my-output_forreports2", width={"size": 2}, style={"margin-left": 0}),
                    dbc.Col([return_sparks(graph1="fig_ppm_forreports", graph2="fig_scrap__forreports",
                                           margin_left=0)],
                            width={"size": 2})], className="d-flex justify-content-center", width=12)
            ], className="g-0")
        ], style={})
    ]),
    dbc.Row([
        dbc.Col(children=[

            dbc.Row(html.H5("Üretim Zaman Çizgisi", style={
                "background-color": "#2149b4",
                "text-align": "center",
                "color": "white",
            })),
            dbc.Row(
                dbc.Col([
                    html.Div(id='gann_forreports')],
                    className="d-flex justify-content-center", width=12)
                , className="g-0")],
            style={}, width={"size": 12}
        ), ]),
    dbc.Row([
        dbc.Col(children=[

            dbc.Row(html.H5("Üretim Duruşları", style={
                "background-color": "#2149b4",
                "text-align": "center",
                "color": "white",
            })),
            dbc.Row(
                dbc.Col([
                    html.Div(id='bubble_forreports')],
                    className="d-flex justify-content-center", width=12)
                , className="g-0")],
            style={}, width={"size": 12}
        ), ]),
    dbc.Row([
        dbc.Col(children=[

            html.H5("Hurda ve Nedenleri", style={
                "height": 25,
                "text-align": "center",
                "background-color": "#2149b4",
                "color": "white",
                "margin-top": "50px"
            }),
            dbc.Row(
                dbc.Col([
                    html.Div(id='fig_scatscrap_forreports')],
                    className="d-flex justify-content-center", width=12)
                , className="g-0")],
            style={}, width={"size": 12}
        ), ])
    ,
    html.Div(id="generated_1graph1data_for_report")]

    , style={"justify-content": "center", "align-items": "center"}, fluid=True)


################################ DATE BUTTONS START  ############################################
################################################################################################


@app.callback(
    Output('location3_forreports', 'href'),
    Input('refresh3_forreports', 'children')
)
def page_refresh3_forreports(n3):
    if n3:
        return "/prodeff"
    return no_update


################################################################################################
################################ DATE BUTTONS END  ############################################
################################################################################################

@app.callback(
    [Output(component_id='my-output_forreports1', component_property='children'),
     Output(component_id='my-output_forreports2', component_property='children')],
    [Input(component_id='work-datees', component_property='data'),
     Input(component_id='oeeelist6', component_property='data')]
)
def return_summary_data(dates, oeeelist6):
    oeeelist6 = pd.read_json(oeeelist6, orient='split')
    df_working_machines = ag.run_query(query=r"EXEC VLFWORKINGWORKCENTERS @WORKSTART=?, @WORKEND=?"
                                       , params=(dates["workstart"], dates["workend"]))
    data1 = ["Production Volume", get_daily_qty(df=oeeelist6)]
    data2 = ["Working Machines",
             working_machinesf(working_machines=df_working_machines)[-1]]
    data3 = ["PPM", get_daily_qty(df=oeeelist6, ppm=True)]
    data4 = ["Scrap", get_daily_qty(df=oeeelist6, type='HURDA')]

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
                            'fontSize': 25, 'text-align': 'left', "margin-top": 65, "margin-left": 0
                            })]


# ------------------------------------------------------------------------------


# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='sunburst_forreports', component_property='children'),
    Input(component_id='oeeelist0', component_property='data')
)
def update_graph_sunburst_forreports(oeeelist0):
    return return_piechart('CNC', oeeelist0,1)


@app.callback(
    Output(component_id='bubble_forreports', component_property='children'),
    Input(component_id='oeeelist2', component_property='data'))
def update_graph_bubble_forreports(oeeelist2):
    graphwidth = 950
    oeeelist2 = pd.read_json(oeeelist2, orient='split')
    df, category_order = scatter_plot(df=oeeelist2.loc[oeeelist2["COSTCENTER"] == 'CNC'])

    # Generate a dynamic color map by assigning colors from Alphabet to each unique 'STEXT' value
    color_map = {category: color for category, color in zip(category_order, px.colors.qualitative.Alphabet)}

    figs = px.histogram(df, x="WORKCENTER", y="FAILURETIME",
                        color="STEXT",
                        hover_data=["WORKCENTER"],
                        color_discrete_map=color_map,category_orders={"STEXT": category_order})
    # figs.update_traces(textfont=dict(family=['Arial Black']))
    figs.update_xaxes(type="category", tickangle=90, fixedrange=True, categoryorder='total ascending'
                      , tickfont=dict(
            color='black',  # Set tick label color to white
            size=13,  # Set font size (adjust as needed)
            family='Arial Black')
                      ),


    # figs.update_yaxes(categoryorder="total descending")
    figs.update_layout(margin=dict(l=100, r=70, t=100, b=100),
                       barmode='overlay',
                       xaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.2)'),
                       yaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.2)'),
                       paper_bgcolor=layout_color, plot_bgcolor=layout_color, font_color=summary_color,
                       title_font_family="Times New Roman", title_font_color="red", width=graphwidth, height=500,
                       showlegend=False,
                       xaxis_title="",
                       yaxis_title=""
                       )

    return html.Div(
        [dbc.Row([
            dbc.Col(
                dcc.Graph(figure=figs), width=10), dbc.Col(legend_generater(color_map, 10), width=2)])])


@app.callback(
    Output(component_id='gann_forreports', component_property='children'),
    Input(component_id='oeeelist2', component_property='data')
)
def update_chart_gann_forreports(oeeelist2):
    graphwidth = 900
    color_map = {"Uretim": "forestgreen", "Plansiz Durus": "red"
        , "Ariza Durusu": "Brown", "Planli Durus": "Coral"
        , "Kurulum": "Aqua"}
    oeeelist2 = pd.read_json(oeeelist2, orient='split')
    df = oeeelist2.loc[oeeelist2["COSTCENTER"] == 'CNC']
    df.sort_values(by="CONFTYPE", ascending=False, inplace=True)
    figs = px.timeline(data_frame=df[["WORKSTART", "WORKEND", "WORKCENTER", "CONFTYPE", "STEXT", "QTY"]],
                       x_start="WORKSTART",
                       x_end="WORKEND",
                       y='WORKCENTER', color="CONFTYPE",
                       color_discrete_map=color_map)


    figs.update_xaxes(type="date", tickangle=90, fixedrange=True, tickfont=dict(
        color='grey',  # Set tick label color to white
        size=13,  # Set font size (adjust as needed)
        family='Arial Black')),

    figs.update_yaxes(categoryorder="category ascending", tickfont=dict(
        color='black',  # Set tick label color to white
        size=13,  # Set font size (adjust as needed)
        family='Arial Black'))
    figs.update_layout(margin=dict(l=100, r=70, t=100, b=100), barmode='overlay', paper_bgcolor=layout_color,
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       font_color=summary_color,
                       title_font_family="Times New Roman", title_font_color="red", width=graphwidth, height=800,
                       showlegend=False,
                       xaxis_title="",
                       yaxis_title=""
                       )

    return html.Div(
        [dbc.Row([
            dbc.Col(
                dcc.Graph(figure=figs), width=10), dbc.Col(legend_generater(color_map,margin_left=20), width=2)])])
    # dcc.Graph(figure=legend_generater(color_map)),


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
                "margin": dict(l=50, r=0, t=4, b=4, pad=0),
                "uirevision": True,
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
                "width": 300,
                "height": 65
            },
        }
    )


@app.callback(
    [Output(component_id='fig_prod_forreports', component_property='figure'),
     Output(component_id='fig_scrap__forreports', component_property='figure'),
     Output(component_id='fig_working_machine_forreports', component_property='figure'),
     Output(component_id='fig_ppm_forreports', component_property='figure')],
    Input(component_id='work-datees', component_property='data'),
    Input(component_id='oeeelist6', component_property='data')
)
def update_spark_line(dates, oeeelist6):
    onemonth_prdqty = pd.read_json(oeeelist6, orient='split')
    df_working_machines = ag.run_query(query=r"EXEC VLFWORKINGWORKCENTERS @WORKSTART=?, @WORKEND=?"
                                       , params=(dates["workstart"], dates["workend"]))
    fig_prod_forreports = get_spark_line(data=generate_for_sparkline(data=onemonth_prdqty, proses='CNC'))
    fig_scrap__forreports = get_spark_line(
        data=generate_for_sparkline(data=onemonth_prdqty, proses='CNC', type='HURDA'))
    fig_working_machine_forreports = get_spark_line(
        data=working_machinesf(working_machines=df_working_machines))
    fig_ppm_forreports = get_spark_line(
        data=generate_for_sparkline(data=onemonth_prdqty, proses='CNC', ppm=True))
    return [fig_prod_forreports, fig_scrap__forreports, fig_working_machine_forreports, fig_ppm_forreports]


@app.callback(
    [Output(component_id='fig_up1_forreports', component_property='figure'),
     Output(component_id='fig_up2_forreports', component_property='figure'),
     Output(component_id='fig_up3_forreports', component_property='figure'),
     Output(component_id='fig_down1_forreports', component_property='figure'),
     Output(component_id='fig_down2_forreports', component_property='figure'),
     Output(component_id='fig_down3_forreports', component_property='figure')
     ],
    Input(component_id='oeeelist1', component_property='data')
)
def update_ind_fig(oeeelist1):
    df = pd.read_json(oeeelist1, orient='split')
    df = df[df["COSTCENTER"] == 'CNC']
    fig_up1_forreports = indicator_with_color(df_metrics=df)
    fig_up2_forreports = indicator_with_color(df_metrics=df, order=1)
    fig_up3_forreports = indicator_with_color(df_metrics=df, order=2)
    fig_down1_forreports = indicator_with_color(df_metrics=df, order=-1, colorof='red')
    fig_down2_forreports = indicator_with_color(df_metrics=df, order=-2, colorof='red')
    fig_down3_forreports = indicator_with_color(df_metrics=df, order=-3, colorof='red')
    return [fig_up1_forreports, fig_up2_forreports, fig_up3_forreports, fig_down1_forreports, fig_down2_forreports,
            fig_down3_forreports]


@app.callback(
    Output(component_id='fig_scatscrap_forreports', component_property='children'),
    Input(component_id='work-datees', component_property='data')
)
def create_scatterplot_for_scrapqty(dates):

    graphwidth = 900
    df_scrap = ag.run_query(query=r"EXEC VLFPRDSCRAPWITHPARAMS @WORKSTART=?, @WORKEND=?"
                            , params=(dates["workstart"], dates["workend"]))
    df_scrap = df_scrap[df_scrap["COSTCENTER"] == 'CNC']
    cat_order_sumscrap = df_scrap.groupby("STEXT")["SCRAP"].sum().sort_values(ascending=False).index
    df_scrap["SCRAP"] = df_scrap["SCRAP"].astype("int")
    category_order = df_scrap["STEXT"].unique()
    color_map = {category: color for category, color in zip(category_order, px.colors.qualitative.Alphabet)}

    fig = px.histogram(data_frame=df_scrap.loc[df_scrap["COSTCENTER"] == 'CNC'],
                       x="WORKCENTER",
                       y="SCRAP",
                       color="STEXT",
                       color_discrete_map=color_map,
                       hover_data=["MTEXTX"],
                       width=1500, height=500,
                       category_orders={"STEXT": cat_order_sumscrap})
    # fig.update_traces(textfont=dict(family=['Arial Black']))
    fig.update_xaxes(type="category", tickangle=90, fixedrange=True, tickfont=dict(
        color='grey',  # Set tick label color to white
        size=13,  # Set font size (adjust as needed)
        family='Arial Black')),    # figs.update_yaxes(categoryorder="total descending")
    fig.update_layout(margin=dict(l=100, r=70, t=100, b=100), barmode='overlay', paper_bgcolor=layout_color,
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       font_color=summary_color,
                       title_font_family="Times New Roman", title_font_color="red", width=graphwidth, height=400,
                       showlegend=False,
                       xaxis_title="",
                       yaxis_title=""
                      )
    return html.Div([dbc.Row([dbc.Col(dcc.Graph(figure=fig), width=10), dbc.Col(legend_generater(color_map,12), width=2, style={'margin-left':0})])])


@app.callback(
    [Output("generated_1graph1data_for_report", "children")],
    [Input("work-datees", "data"),
     Input(component_id='oeeelist1', component_property='data'),
     Input(component_id='oeeelist3', component_property='data'),
     Input(component_id='oeeelist7', component_property='data')])
def update_ind_fig(params, oeeelist1w, oeeelist3w, oeeelist7w):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_wcs (list): The list of work centers to display.
        option_slctd = 'CNC' (str): The selected cost center.
        report_day (str): The date for which to display the report. Default is "2022-07-26".

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.

    Parameters
    ----------
    oeeelist7w
    oeeelist3w
    params
    report_type
    option_slctd = 'CNC'
    oeeelist1w
    """

    params["interval"] = 'day'

    def return_layout(report_type='wc'):
        list_of_figs, list_of_data, list_of_columns, list_of_styles = workcenters('CNC', report_type,
                                                                                  params,
                                                                                  oeeelist1w, oeeelist3w, oeeelist7w)

        def create_column(fig, data, columns, margin_left):
            return dbc.Col(
                [dbc.Row(
                    dcc.Graph(figure=fig, style={'margin-left': 150, 'margin-bottom': 300})),
                dbc.Row(
                    dash_table.DataTable(
                        data=data,
                        columns=columns,
                        style_cell={
                            'color': 'black',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'minWidth': '20px', 'width': '80px', 'maxWidth': '60px',
                            'textAlign': 'center',
                            'border': '1px solid black',
                            'minWidth': '80px', 'maxWidth': '300px',
                            'fontSize': '12px'
                        },
                        style_table={
                            'height': '150px',
                            'width': '800px',
                            'overflowY': 'auto',
                            'borderCollapse': 'collapse',
                            'border': '1px solid black'
                        },
                        style_header={
                            'fontWeight': 'bold',
                            'backgroundColor': 'rgba(0, 0, 0, 0.1)',
                            'borderBottom': '1px solid black',
                            'color': 'black'
                        },
                        style_data_conditional=[]
                    ), style={'margin-top': 70})
                ],
                width=4,
                style={"justify-content": "center",
                       "margin-left": margin_left, "width": 600}
            )

        # This list comprehension creates all columns needed for the layout
        columns = [create_column(list_of_figs[i], list_of_data[i], list_of_columns[i], 0 if i % 2 == 0 else 300) for i
                   in range(len(list_of_figs))]

        # This code groups the columns into rows of 3 columns each
        rows = [dbc.Row(columns[i:i + 2],style={"margin-bot":150}) for i in range(0, len(columns), 2)]

        layout = html.Div(children=rows,style={"margin-bot":400})

        return layout

    return [html.Div(children=[html.H3("İş Merkezi Göstergeleri", style={
        "height": 35,
        "text-align": "center",
        "background-color": "#b6b8bf",
        "color": "white",
        "margin-top": "50px"
    }), return_layout("wc"), html.H3("Personel Göstergeleri", style={
        "height": 35,
        "text-align": "center",
        "background-color": "#b6b8bf",
        "color": "white",
        "margin-top": "50px"
    }), return_layout("pers")])]
