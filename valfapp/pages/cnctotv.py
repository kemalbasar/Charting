from datetime import date, timedelta, datetime
from valfapp.app import workcenters, app, prdconf, return_piechart
import dash_table
import json
import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import return_indicatorgraph
from valfapp.app import app
from config import project_directory
from run.agent import ag

costcenters = ["CNC", "CNCTORNA", "TASLAMA", "MONTAJ", "PRESHANE1", "PRESHANE2"]
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

fig, data, columns, styles = workcenters("CNCTORNA", "pers", params_dic, oeelist1w, oeelist3w, oeelist7w)
# alt satırı app.workcennter metoduna taşımak gerek
fig = [i for i in fig if i != {}]
maxof_slide = len(fig)

layout =dbc.Row([
        # First Column
        dbc.Col([
            html.Div(id="wc-output-container",className= "row g-0"),
            # Other components for this column
        ], width=8),

        # Second Column
        dbc.Col([
            dbc.Row([
                dcc.Graph(figure=return_piechart("CNCTORNA", oeelist0w))
            ],className="g-0"),
            dbc.Row([
                html.Button("Play", id="play", style={'width': '90px'}),
                dcc.Slider(
                    min=0,
                    max=len(fig),
                    step=1,
                    value=0,
                    id='wc-slider'
                ),
                html.Div(
                    id='slider-output-container',className= "row g-0"
                ),
                dcc.Interval(id="animate", interval=10000, disabled=True),
                dcc.Store(id="list_of_stationss"),
                dcc.Store(
                    id="livedata",
                    data=ag.run_query(project_directory + r"\Charting\queries\liveprd.sql").to_json(date_format='iso',
                                                                                    orient='split')
                ),
            ]),
        ], width=4),
    ],className="g-0")


@app.callback(
    Output("animate", "disabled"),
    Input("play", "n_clicks"),
    State("animate", "disabled"),
)
def toggle(n, playing):
    print("****888*****")
    print(n)
    if n:
        return not playing
    return playing


@app.callback(
    Output('slider-output-container', 'children'),
    Output("wc-slider", "value"),
    Output("livedata", "data"),
    Input("animate", "n_intervals"),
    Input("wc-slider", "value"),
    prevent_initial_call=True,
)
def update_output(n, selected_value):
    list_of_figs, list_of_data, list_of_columns, list_of_styles = workcenters("CNCTORNA", "pers", params_dic, oeelist1w,
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
        ), selected_value + 1,ag.run_query(project_directory + r"\Charting\queries\liveprd.sql").to_json(date_format='iso',
                                                                                    orient='split')
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
        ), selected_value + 1,no_update


# Import required libraries and modules

# Define constants and initial data


# Create the layout for the app
# layout = dbc.Container([
#
#     dcc.Link(
#         children='Main Page',
#         href='/',
#         style={"color": "black", "font-weight": "bold"}
#
#     ),
#     # dcc.Dropdown(id="costcenter",
#     #              options=[{"label": cc, "value": cc} for cc in costcenters],
#     #              multi=False,
#     #              value="CNC",
#     #              style={"color": "green", "background-color": "DimGray", 'width': 200}
#     #              ),
#
#
# ], fluid=True)


@app.callback(
    Output('wc-output-container', 'children'),
    Input("animate", "n_intervals"),
    Input("wc-slider", "value"),
    State("livedata", 'data')
)
def update_ind_fig(n, selected_value, livedata):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_stationss (list): The list of work centers to display.

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.
    """
    df = pd.read_json(livedata, orient='split')
    df = df[df["COSTCENTER"] == "CNCTORNA"].reset_index(drop=True)

    list_of_figs = []
    list_of_stationss = []
    for item in df.loc[df["COSTCENTER"] == "CNCTORNA"]["WORKCENTER"].unique():
        list_of_stationss.append(item)
    for index, row in df.iterrows():
        if index < len(list_of_stationss):
            fig = return_indicatorgraph(row["STATUSR"], row["FULLNAME"], row["WORKCENTER"], row["DRAWNUM"],
                                        row["STEXT"], 0)

            list_of_figs.append(fig)

        else:
            fig = {}
            style = {"display": "none"}

    lengthof = len(list_of_figs)
    x = lengthof % 4
    newlengthof = lengthof - x
    numofforths = newlengthof / 4
    counter = 0

    listofdivs = []
    for i in range(0, len(list_of_figs), 4):
        if counter != numofforths:
            listofdivs.append(html.Div([
                dbc.Row([
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i])),width=4),
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 1])),width=4)
                ],className="g-0"),
                dbc.Row([
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 2])),width=4),
                    dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 3])),width=4),
                ],className="g-0")
            ]))
        else:
            if x == 0:
                continue
            else:
                print("here")
                listofdivs.append(html.Div([
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i])),width=4),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 1] if x > 1 else {})),width=4)
                    ],className="g-0"),
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 2] if x > 2 else {})),width=4),
                        dbc.Col(html.Div(dcc.Graph(figure=list_of_figs[i + 3] if x > 3 else {})),width=4),
                    ],className="g-0")
                ]))
        counter = counter + 1
    print("****")
    print(len(listofdivs))
    selected_value = selected_value%len(listofdivs)
    print(selected_value)
    print("******")
    return listofdivs[selected_value]
