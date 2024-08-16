import json
from datetime import date, timedelta, datetime

import pandas as pd

from valfapp.app import workcenters, app, prdconf, return_piechart
from valfapp.layouts import layout_for_tvs
import dash_table
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from config import project_directory
from run.agent import ag
from valfapp.layouts import sliding_indicator_container
from valfapp.app import cache

today = datetime.today()

if today.weekday() == 6:
    kb = 2
elif today.weekday() == 0:
    kb = 3
else:
    kb = 1

params_list = [(date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"]

layout = layout_for_tvs(costcenter='CNC1')

@app.callback(
    Output("animate_cnc1", "disabled"),
    Input("play", "n_clicks"),
    State("animate_cnc1", "disabled"),
)
def toggle(n, playing):
    print("****888*****")
    print(n)
    if n:
        return not playing
    return playing


@app.callback(
    Output('slider-output-container_cnc1', 'children'),
    Output("wc-slider_cnc1", "value"),
    Output("livedata_cnc1", "data"),
    Output("wc-slider_cnc1", "max"),
    Input("animate_cnc1", "n_intervals"),
    Input("wc-slider_cnc1", "value"),
    State(component_id='oeelist1w_tv_cnc1', component_property='data'),
    State(component_id='oeelist3w_tv_cnc1', component_property='data'),
    State(component_id='oeelist7w_tv_cnc1', component_property='data'),
    prevent_initial_call=True,
)
def update_output(n, selected_value, oeelist1w, oeelist3w, oeelist7w):
    print("buradayız")
    params_dic = {"workstart": (date.today() - timedelta(days=kb)).isoformat(),
                  "workend": date.today().isoformat(),
                  "interval": "day"}


    list_of_figs, list_of_data, list_of_columns, list_of_styles = workcenters("CNC1", "pers", params_dic, oeelist1w,
                                                                              oeelist3w, oeelist7w,1)
    print(" burada mıyız ????? ")
    list_of_figs = [i for i in list_of_figs if i != {}]
    max_of_slider = len(list_of_figs)

    print("asdadasdasda")
    print(list_of_data)
    print("asdadasdasda")

    if selected_value + 1 > len(list_of_figs):
        selected_value = -1
        return html.Div(
            children=[
                dcc.Graph(figure=list_of_figs[selected_value],style={'margin-left':'107px'}),
                dash_table.DataTable(data=list_of_data[selected_value], columns=list_of_columns[selected_value],
                                     style_cell={
                                         "minWidth": "80px",
                                         "width": "80px",
                                         "maxWidth": "100px",
                                         "textAlign": "center",
                                     },
                                     style_table={
                                         "height": '150px',
                                         "width": '300px',  # Fixed pixel width
                                         "overflowY": 'auto',
                                     }
                                     )
            ],style={'margin-left': '-180px'}
        ), selected_value + 1, ag.run_query(project_directory + r"\Charting\queries\liveprd.sql") \
            .to_json(date_format='iso', orient='split'), max_of_slider
    else:
        return html.Div(
            children=[
                dcc.Graph(figure=list_of_figs[selected_value],style={'margin-left':'107px'}),
                dash_table.DataTable(data=list_of_data[selected_value],
                                     columns=list_of_columns[selected_value],
                                     style_cell={
                                         'color': 'black',  # Font color for the cells
                                         'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                                         # Slightly transparent background
                                         'minWidth': '80px', 'width': '80px', 'maxWidth': '100px',
                                         # Cell width specifications
                                         'textAlign': 'center',  # Center text alignment
                                         'border': '1px solid black'  # Border for the cells
                                     },
                                     style_table={
                                         'height': '150px',  # Fixed height for the virtualized table
                                         'width': '800px',  # Fixed width for the table
                                         'overflowY': 'auto',  # Enable vertical scroll
                                         'borderCollapse': 'collapse',  # Collapse borders
                                         'border': '1px solid black'  # Border around the table
                                     },
                                     style_header={
                                         'fontWeight': 'bold',  # Make header text bold
                                         'backgroundColor': 'rgba(0, 0, 0, 0.1)',
                                         # Slightly darker background for the header
                                         'borderBottom': '1px solid black',  # Bottom border for the header cells
                                         'color': 'black'  # Font color for the header
                                     },
                                     style_data_conditional=[
                                         # Here you can add any conditional styles you might have
                                         # For example, styling for the active cell or conditional formatting based on cell values
                                     ],
                                     )
            ]
        , style={'margin-left': '-180px'}), selected_value + 1, no_update, max_of_slider


@app.callback(
    Output('wc-output-container_cnc1', 'children'),
    Input("animate_cnc1", "n_intervals"),
    Input("wc-slider_cnc1", "value"),
    State("livedata_cnc1", 'data')
)
def update_ind_fig(n, selected_value, livedata_cnc1):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_stationss (list): The list of work centers to display.

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.
    """

    return sliding_indicator_container(livedata=livedata_cnc1,
                                       selected_value=selected_value, costcenter='CNC1')


@app.callback(
    Output("oeelist1w_tv_cnc1", "data"),
    Output('oeelist3w_tv_cnc1', 'data'),
    Output('oeelist7w_tv_cnc1', 'data'),
    Output('oeelist0w_tv_cnc1', 'data'),
    Input("15min_update", "n_intervals"))
def refresh_data(n):
    params_dic = {"workstart": (date.today() - timedelta(days=kb)).isoformat(),
                  "workend": date.today().isoformat(),
                  "interval": "day"}
    # a = cache.get(json.dumps({'workstart': '2023-09-06', 'workend': '2023-09-07', 'interval': 'day'}))
    # cache_key = json.dumps(params_dic)
    # x = cache.get(params_dic)
    cache.delete_memoized(prdconf, (params_dic["workstart"], params_dic["workend"], params_dic["interval"]))
    oeelist1w = prdconf(params_list)[1]
    oeelist3w = prdconf(params_list)[3]
    oeelist7w = prdconf(params_list)[7]
    oeelist0w = prdconf(params_list)[0]
    return  oeelist1w,oeelist3w,oeelist7w,oeelist0w
    #
    # fig, data, columns, styles = workcenters("MONTAJ", "pers", params_dic, oeelist1w, oeelist3w, oeelist7w)
    # alt satırı app.workcennter metoduna taşımak gerek


@app.callback(
    Output('pie_of_yesterday_cnc1', 'figure'),
    Input("oeelist0w_tv_cnc1", "data"),
    Input("play", "n_clicks"))
def update_piechart(oeelist0w,n):
    print(oeelist0w)
    return return_piechart("CNCTORNA", oeelist0w)
