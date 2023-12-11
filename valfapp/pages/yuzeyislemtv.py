from datetime import date, timedelta, datetime
from valfapp.app import workcenters, app, prdconf, return_piechart
import dash_table
import json
import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import return_indicatorgraph, return_DELTAgraph
from valfapp.app import app
from config import project_directory
from run.agent import ag


len_fig = int(len(ag.run_query(project_directory + r"\Charting\queries\yuzeyislemtvsorgu.sql"))/8) +1


layout =[dcc.Link(
        children='Main Page',
        href='/',
        style={"height":40,"color": "black", "font-weight": "bold"}

    ),
        dcc.Store(id="list_of_stationss"),
        dcc.Store(id="livedata_yislem",data=ag.run_query(project_directory +
             r"\Charting\queries\yuzeyislemtvsorgu.sql").to_json(date_format='iso',orient='split')),
        dcc.Interval(id="animate_yislem", interval=10000, disabled=True),
         dbc.Col([
            dbc.Row([html.Div(id="wc-output-container_yislem",className= "g-0"),]),
            dbc.Row([
                html.Button("Play", id="play", style={'width': '90px'}),
                dcc.Slider(
                    min=0,
                    max=len_fig,
                    step=1,
                    value=-1,
                    id='wc-slider_yislem'
                ),
                dcc.Interval(id="animate_yislem", interval=10000, disabled=True)
            ],className= "g-0"),


        ], width=12),
    ]



@app.callback(
    Output("animate_yislem", "disabled"),
    Input("play", "n_clicks"),
    State("animate_yislem", "disabled"),
)
def toggle(n, playing):
    print("****888*****")
    print(n)
    if n:
        return not playing
    return playing



@app.callback(
    Output('wc-output-container_yislem', 'children'),
    Output("wc-slider_yislem", "value"),
    Output("livedata_yislem", 'data'),
    Input("animate_yislem", "n_intervals"),
    State("wc-slider_yislem", "value"),
    State("livedata_yislem", 'data')
)
def update_ind_fig(n, selected_value, livedata_yislem):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_stationss (list): The list of work centers to display.

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.
    """
    df = pd.read_json(livedata_yislem, orient='split')
    # df = df[df["COSTCENTER"] == "YUZEYISLEM"].reset_index(drop=True)

    list_of_figs = []
    list_of_stationss = []
    for item in df.loc[df["COSTCENTER"] != "YUZEYIsSLEM"]["WORKCENTER"].unique():
        list_of_stationss.append(item)
    for index, row in df.iterrows():
        if index < len(list_of_stationss):
            fig = return_DELTAgraph(row["STATUSR"], row["FULLNAME"], row["WORKCENTER"], row["DRAWNUM"],
                                        row["STEXT"], row["TARGET"])

            list_of_figs.append(fig)

        else:
            fig = {}
            style = {"display": "none"}

    lengthof = len(list_of_figs)
    x = lengthof % 8
    newlengthof = lengthof - x
    numofforths = newlengthof / 8
    counter = 0

    listofdivs = []
    for i in range(0, len(list_of_figs), 8):
        if counter != numofforths:
            listofdivs.append(html.Div([
                dbc.Row([
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i])),width=3),
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 1])),width=3),
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i+2])),width=3),
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 3])),width=3)
                ],className="g-0"),
                dbc.Row([
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 4])),width=3),
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 5])),width=3),
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 6])),width=3),
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 7])),width=3),
                ],className="g-0")
            ]))
        else:
            if x == 0:
                continue
            else:
                print("here")
                listofdivs.append(html.Div([
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i])),width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 1] if x > 1 else {})),width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i+2] if x > 2 else {})),width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 3] if x > 3 else {})),width=3)
                    ],className="g-0"),
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 4] if x > 4 else {})),width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 5] if x > 5 else {})),width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 6] if x > 6 else {})),width=3),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 7] if x > 7 else {})),width=3),
                    ],className="g-0")
                ]))
        counter = counter + 1

    selected_value = selected_value%len(listofdivs)
    if selected_value == 0:
        return listofdivs[selected_value],selected_value + 1,ag.run_query(project_directory +
             r"\Charting\queries\yuzeyislemtvsorgu.sql").to_json(date_format='iso',orient='split')
    else:
        return listofdivs[selected_value], selected_value + 1, no_update
