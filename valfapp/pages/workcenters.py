# Import required libraries and modules
import numpy as np
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components.themes import PULSE
from valfapp.functions.functions_prd import return_ind_fig
import plotly.express as px
from valfapp.app import cache, oee, app
import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import io

from dash_table.Format import Format, Scheme

from config import project_directory
from run.agent import ag

# Define constants and initial data
MAX_OUTPUT = 50
costcenters = ["CNC", "CNCTORNA", "TASLAMA", "MONTAJ","PRESHANE1","PRESHANE2"]
oeelist = oee()


def generate_output_list(max_output):
    """
    Generates a list of Output elements for the Dash app.

    Args:
        max_output (int): The maximum number of output elements to generate.

    Returns:
        list: A list of Output elements.
    """
    return [Output(f"wc{i + 1}_graph", "figure") for i in range(max_output)] + \
           [Output(f"wc{i + 1}_table", "data") for i in range(max_output)] + \
           [Output(f"wc{i + 1}_table", "columns") for i in range(max_output)] + \
           [Output(f"wc{i + 1}", "style") for i in range(max_output)]


def return_tops_with_visibility(graph_id, visible=True):
    """
    Creates a Dash HTML Div containing a Graph and DataTable with optional visibility.

    Args:
        graph_id (str): The base identifier for the Graph and DataTable elements.
        visible (bool): Whether the Div should be visible initially. Default is True.

    Returns:
        html.Div: A Dash HTML Div containing the Graph and DataTable.
    """
    return html.Div(
        children=[
            dcc.Graph(id=f"{graph_id}_graph", figure={}),
            dash_table.DataTable(id=f"{graph_id}_table", data=[], columns=[],
                                 style_cell={
                                     "minWidth": "80px",
                                     "width": "80px",
                                     "maxWidth": "100px",
                                     "textAlign": "center",
                                 },
                                 )
        ],
        id=graph_id,
        style={"display": "flex", "flex-direction": "column","justify-content": "space-between",
               "margin-top": 100,"align-items": "center", "width": 1200},
        hidden=not visible
    )


# def create_pie_chart(df, costcenter):
#     """
#     Creates a pie chart showing the rate of rows with FLAG_BADDATA = 1 to FLAG_BADDATA = 0
#     for the selected cost center.
#
#     Args:
#         df (DataFrame): The input DataFrame containing the FLAG_BADDATA and COSTCENTER columns.
#         costcenter (str): The selected cost center.
#
#     Returns:
#         plotly.graph_objs.Figure: A Plotly Figure object representing the pie chart.
#     """
#     df_filtered = df[df["COSTCENTER"] == costcenter]
#     flag_counts = df_filtered["FLAG_BADDATA"].value_counts()
#     labels = ["0 - Valid Data", "1 - Invalid Data"]
#     values = [flag_counts.get(0, 0), flag_counts.get(1, 0)]
#
#     fig = px.pie(names=labels, values=values, title="Data Validity Distribution")
#     return fig


# Create the layout for the app
layout = dbc.Container([
    dcc.Store(id="list_of_wcs"),
    dcc.Link(
        children='Main Page',
        href='/',
        style={"color": "black", "font-weight": "bold"}
    ),
    dbc.Row([dbc.InputGroup([
        dcc.Dropdown(id="costcenter",
                     options=[{"label": cc, "value": cc} for cc in costcenters],
                     multi=False,
                     value="CNC",
                     style={'width': 150,'font':'purple','backgroundColor':'#593196'}
                     )
    ],style={'width': 150,'font':'purple'}),
        html.Button("Download Data", id="download-button", n_clicks=0, className="bbtn btn-primary btn-sm ml-auto",
        style={"position": "absolute", "right": "0", "top": "-1", "width": "150px", "height": "35px"}),
        dcc.Download(id="download-data")],style= {"margin-top":10}),
    html.Div(id="toggle_div", children=[
        html.H1("Hatalı Veri Girişleri", style={"textAlign": "center"}),
        html.Hr(),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id="pie_chart", figure={}),
                width={"size": 4}
            ),
            dbc.Col(
                dash_table.DataTable(
                    id="invalid_data_table",
                    columns=[{"name": i, "id": i} for i in oeelist[4].columns],
                    style_cell={
                        "minWidth": "100px",
                        "width": "100px",
                        "maxWidth": "400px",
                        "textAlign": "center",
                    },
                ),
                width={"size": 8}
            ),
        ]),
        html.Hr(),
    ]),
    html.Hr(),
    dbc.Button("Hataları Gizle", id="toggle_button", n_clicks=0, className="mr-2"),
    dbc.Row(
        [dbc.Col(return_tops_with_visibility(f"wc{i + 1}"), width="6") for i in range(MAX_OUTPUT)],
        justify="start"
    )
], fluid=True)


list_of_callbacks = generate_output_list(MAX_OUTPUT)

# Callback for hiding/showing the first div
@app.callback(
    Output("toggle_div", "style"),
    Input("toggle_button", "n_clicks")
)
def toggle_first_div(n_clicks):
    if n_clicks and n_clicks % 2 == 1:
        return {"display": "none"}
    else:
        return {}


@app.callback(
    Output("pie_chart", "figure"),
    Input("costcenter", "value")
)
def update_pie_chart(costcenter):
    df = oeelist[5]
    df_filtered = df.loc[df["COSTCENTER"] == costcenter]
    labels = ["0 - Geçerli Data", "1 - Tanımlı Süre Yok", "2 - Hatalı Operatör Girişi", "3 - Tanımlı Süre Hatalı"]
    values = [0 if len(df_filtered[df_filtered["BADDATA_FLAG"] == 0]) == 0 else
              int(df_filtered[df_filtered["BADDATA_FLAG"] == 0]["SUMS"]),
              0 if len(df_filtered[df_filtered["BADDATA_FLAG"] == 1]) == 0 else
              int(df_filtered[df_filtered["BADDATA_FLAG"] == 1]["SUMS"]),
              0 if len(df_filtered[df_filtered["BADDATA_FLAG"] == 2]) == 0 else
              int(df_filtered[df_filtered["BADDATA_FLAG"] == 2]["SUMS"]),
              0 if len(df_filtered[df_filtered["BADDATA_FLAG"] == 3]) == 0 else \
                  int(df_filtered[df_filtered["BADDATA_FLAG"] == 3]["SUMS"])
              ]

    fig = px.pie(names=labels, values=values, title="Veri Geçerlilik Dağalımı")
    return fig


# Callback for the table data based on the selected cost center
@app.callback(
    Output("invalid_data_table", "data"),
    Input("costcenter", "value")
)
def update_table_data(costcenter):
    """
    Generates table data for rows with FLAG_BADDATA = 1 for the selected cost center.

    Args:
        costcenter (str): The selected cost center.
6+


    Returns:
        list: A list of dictionaries representing the table data.
    """
    df_filtered = oeelist[4][oeelist[4]["COSTCENTER"] == costcenter]
    return df_filtered.to_dict("records")


@app.callback(
    Output("list_of_wcs", "value"),
    Input("costcenter", "value")
)
def update_work_center_list(option_slctd):
    """
    Callback to update the list of work centers based
    on the selected cost center.

    Args:
        option_slctd (str): The selected cost center.

    Returns:
        list: A list of work centers for the selected cost center.
    """
    list_of_wcs = []
    for item in oeelist[1].loc[oeelist[1]["COSTCENTER"] == option_slctd]["WORKCENTER"].unique():
        list_of_wcs.append(item)
    return list_of_wcs


@app.callback(
    [*list_of_callbacks],
    Input("list_of_wcs", "value"),
    Input("costcenter", "value")
)
def update_ind_fig(list_of_wcs, option_slctd, report_day="2022-07-26"):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_wcs (list): The list of work centers to display.
        option_slctd (str): The selected cost center.
        report_day (str): The date for which to display the report. Default is "2022-07-26".

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.
    """
    df = oeelist[1][oeelist[1]["COSTCENTER"] == option_slctd]
    df_wclist = oeelist[3][oeelist[3]["COSTCENTER"] == option_slctd]
    list_of_figs = []
    list_of_columns = []
    list_of_data = []
    list_of_styles = []

    for item in range(MAX_OUTPUT):
        if item < len(list_of_wcs):
            fig = return_ind_fig(df_metrics=df,df_details=df_wclist,
                                 costcenter=option_slctd, order=list_of_wcs[item], colorof='black')

            df_details = df_wclist.loc[(df_wclist["WORKCENTER"] == list_of_wcs[item]),
                                       ["SHIFT", "MATERIAL", "QTY", "AVAILABILITY", "PERFORMANCE","QUALITY", "OEE","TOTALTIME"]]
            if len(df_details) == 0:
                continue

            columns = [{"name": i, "id": i} for i in df_details.columns]
            data = df_details.to_dict("records")
            style = {"display": "flex", "justify-content": "space-between",
                     "align-items": "center", "width": 700,
                     "height": 250}
            # df_details.sort_values(by=["SHIFT"], inplace=True)

            weights = df_details.loc[df_details.index, "TOTALTIME"]
            weights[weights <= 0] = 1
            def weighted_average(x):
                # Use the updated weights
                return np.average(x, weights=weights.loc[x.index])
            wm = lambda x: weighted_average(x)
            aggregations = {
                'MATERIAL': max,  # Sum of 'performance' column
                'QTY': "sum",  # Mean of 'availability' column
                'AVAILABILITY' : wm,
                'PERFORMANCE': wm,
                'QUALITY':wm,
                'OEE':wm,
                'SHIFT':'count'
            }
            # Burada vardiya özet satırını oluşturup ekliyoruz.
            summary_row = df_details.groupby('SHIFT').agg(aggregations)
            summary_row = summary_row[summary_row["SHIFT"] > 1]
            summary_row["SHIFT"] = summary_row.index
            summary_row["SHIFT"] = summary_row["SHIFT"].astype(str)
            summary_row["SHIFT"] = summary_row["SHIFT"] + ' (Özet)'
            df_details=df_details.append(summary_row)
            # Verileri yüzde formuna getiriyoruz
            df_details= df_details.drop(["TOTALTIME"], axis=1)
            df_details["AVAILABILITY"] = (df_details["AVAILABILITY"] * 100).round()
            df_details["AVAILABILITY"] = df_details["AVAILABILITY"].astype(str) + '%'
            df_details["QUALITY"] = (df_details["QUALITY"] * 100).round()
            df_details["QUALITY"] = df_details["QUALITY"].astype(str) + '%'
            df_details["OEE"] = (df_details["OEE"] * 100).round()
            df_details["OEE"] = df_details["OEE"].astype(str) + '%'
            df_details["PERFORMANCE"] = (df_details["PERFORMANCE"] * 100).round()
            df_details["PERFORMANCE"] = df_details["PERFORMANCE"].astype(str) + '%'
            style = {"display": "flex", "justify-content": "space-between",
                     "align-items": "center", "width": 700,
                     "height": 250}
            df_details["SHIFT"] = df_details["SHIFT"].astype(str)
            df_details.sort_values(by='SHIFT', inplace=True)
            columns = [{"name": i, "id": i} for i in df_details.columns]
            data = df_details.to_dict("records")


        else:
            fig = {}
            columns = []
            data = []
            style = {"display": "none"}

        list_of_figs.append(fig)
        list_of_data.append(data)
        list_of_columns.append(columns)
        list_of_styles.append(style)

    return tuple(list_of_figs + list_of_data + list_of_columns + list_of_styles)

@app.callback(
    Output("download-data", "data"),
    [Input("download-button", "n_clicks")],
    [Input("costcenter", "value")],
)
def generate_excel(n_clicks, costcenter):
    if n_clicks < 1:
        raise PreventUpdate

    dff = oeelist[3][oeelist[3]["COSTCENTER"] == costcenter]

    return dcc.send_data_frame(dff.to_excel, "mydata.xlsx", index=False)



