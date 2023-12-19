from datetime import date, timedelta, datetime
from valfapp.app import workcenters, app, prdconf, return_piechart
import dash_table
import json
import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import indicator_for_tvs
from valfapp.app import app
from config import project_directory
from run.agent import ag
from valfapp.layouts import sliding_indicator_container

today = datetime.today()

if today.weekday() == 6:
    kb = 2
elif today.weekday() == 0:
    kb = 3
else:
    kb = 1

params_dic = {"workstart": (date.today() - timedelta(days=kb)).isoformat(),
              "workend": date.today().isoformat(),
              "interval": "day"}
params_list = [(date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"]

oeelist1w = prdconf(params_list)[1]
oeelist3w = prdconf(params_list)[3]
oeelist7w = prdconf(params_list)[7]
oeelist0w = prdconf(params_list)[0]

fig, data, columns, styles = workcenters("TASLAMA", "pers", params_dic, oeelist1w, oeelist3w, oeelist7w)
# alt satırı app.workcennter metoduna taşımak gerek
fig = [i for i in fig if i != {}]
maxof_slide = len(fig)

layout =dbc.Row([
        # First Column
        dbc.Col([
            html.Div(id="wc-output-container_taslama",className= "row g-0"),
            # Other components for this column
        ], width=8),

        # Second Column
        dbc.Col([
            dbc.Row([
                dcc.Graph(id= 'pie_taslama',figure=return_piechart("TASLAMA", oeelist0w))
            ],className="g-0"),
            dbc.Row([
                html.Button("Play", id="play", style={'width': '90px'}),
                dcc.Slider(
                    min=0,
                    max=len(fig),
                    step=1,
                    value=0,
                    id='wc-slider_taslama'
                ),
                html.Div(
                    id='slider-output-container_taslama',className= "row g-0"
                ),
                dcc.Interval(id="animate_taslama", interval=10000, disabled=True),
                dcc.Store(id="list_of_stationss"),
                dcc.Store(
                    id="livedata_taslama",
                    data=ag.run_query(project_directory + r"\Charting\queries\liveprd.sql").to_json(date_format='iso',
                                                                                    orient='split')
                ),
            ]),
        ], width=4),
    ],className="g-0")


@app.callback(
    Output("animate_taslama", "disabled"),
    Input("play", "n_clicks"),
    State("animate_taslama", "disabled"),
)
def toggle(n, playing):
    print("****888*****")
    print(n)
    if n:
        return not playing
    return playing


@app.callback(
    Output('slider-output-container_taslama', 'children'),
    Output("wc-slider_taslama", "value"),
    Output("livedata_taslama", "data"),
    Output('pie_taslama', 'figure'),
    Input("animate_taslama", "n_intervals"),
    Input("wc-slider_taslama", "value"),
    prevent_initial_call=True,
)
def update_output(n, selected_value):
    list_of_figs, list_of_data, list_of_columns, list_of_styles = workcenters("TASLAMA", "pers", params_dic, oeelist1w,
                                                                              oeelist3w, oeelist7w)
    list_of_figs = [i for i in list_of_figs if i != {}]

    if selected_value + 1 > len(list_of_figs):
        selected_value = -1
        return html.Div(
            children=[
                dcc.Graph(figure=list_of_figs[selected_value], style={'margin-left': 120}),
                dash_table.DataTable(data=list_of_data[selected_value], columns=list_of_columns[selected_value],
                                     style_cell={
                                         "minWidth": "80px",
                                         "width": "80px",
                                         "maxWidth": "100px",
                                         "textAlign": "center",
                                     },
                                     style_table={
                                         "height": '150px',
                                         "width": '700px',  # Fixed pixel width
                                         "overflowY": 'auto',
                                     }
                                     )
            ]
        ), selected_value + 1,ag.run_query(project_directory
       + r"\Charting\queries\liveprd.sql").to_json(date_format='iso',orient='split'),

    else:
        return html.Div(
            children=[
                dcc.Graph(figure=list_of_figs[selected_value]),
                dash_table.DataTable(data=list_of_data[selected_value], columns=list_of_columns[selected_value],
                                     style_cell={
                                         "minWidth": "80px",
                                         "width": "80px",
                                         "maxWidth": "100px",
                                         "textAlign": "center",
                                     },
                                     style_table={
                                         "height": '150px',
                                         "width": '700px',  # Fixed pixel width
                                         "overflowY": 'auto',
                                     }
                                     )
            ]
        ), selected_value + 1,no_update,no_update


@app.callback(
    Output('wc-output-container_taslama', 'children'),
    Input("animate_taslama", "n_intervals"),
    Input("wc-slider_taslama", "value"),
    State("livedata_taslama", 'data')
)
def update_ind_fig(n, selected_value, livedata_taslama):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_stationss (list): The list of work centers to display.

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.
    """

    return sliding_indicator_container(livedata = livedata_taslama,selected_value= selected_value,costcenter= 'TASALAMA')


