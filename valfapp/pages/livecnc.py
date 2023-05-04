# Import required libraries and modules
import pandas as pd
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import return_indicatorgraph
import plotly.express as px
from valfapp.app import cache, oee, app
import dash_table
from config import project_directory
from run.agent import ag
# Define constants and initial data
MAX_OUTPUT = 29
costcenters = ["CNC", "CNCTORNA", "TASLAMA", "MONTAJ"]

df = ag.run_query(project_directory + r"\Charting\queries\liveprd.sql")


def generate_output_list(max_output):
    """
    Generates a list of Output elements for the Dash app.

    Args:
        max_output (int): The maximum number of output elements to generate.

    Returns:
        list: A list of Output elements.
    """
    return [Output(f"stations{i + 1}_graph", "figure") for i in range(max_output)] + \
           [Output(f"stations{i + 1}", "style") for i in range(max_output)]


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
        ],
        id=graph_id,
        style={"display": "flex", "justify-content": "flex-start",
               "align-items": "center"},
        hidden=not visible
    )




# Create the layout for the app
layout = dbc.Container([
    dcc.Store(id="list_of_stationss"),
    dcc.Link(
        children='Main Page',
        href='/',
        style={"color": "black", "font-weight": "bold"}

    ),
    dcc.Dropdown(id="costcenter",
                     options=[{"label": cc, "value": cc} for cc in costcenters],
                     multi=False,
                     value="CNC",
                     style={"color": "green", "background-color": "DimGray", 'width': 200}
                     ),

    dbc.Row(
        [
            dbc.Col(return_tops_with_visibility(f"stations{i + 1}")) for i in range(MAX_OUTPUT)],
        justify="start",
        className="row-cols"
    )
], fluid=True)

list_of_callbacks = generate_output_list(MAX_OUTPUT)




@app.callback(
    Output("list_of_stationss", "value"),
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
    list_of_stationss = []
    for item in df.loc[df["COSTCENTER"] == option_slctd]["WORKCENTER"].unique():
        list_of_stationss.append(item)
    print(list_of_stationss)
    return list_of_stationss

@app.callback(
    [*list_of_callbacks],
    Input("list_of_stationss", "value"),
    Input("costcenter", "value")
)
def update_ind_fig(list_of_stationss, option_slctd, report_day="2022-07-26"):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_stationss (list): The list of work centers to display.
        option_slctd (str): The selected cost center.
        report_day (str): The date for which to display the report. Default is "2022-07-26".

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.
    """
    global df
    df = df[df["COSTCENTER"] == option_slctd].reset_index(drop=True)
    print(df)

    list_of_figs = []
    list_of_styles = []

    for index, row in df.iterrows():
        if index < len(list_of_stationss):
            fig = return_indicatorgraph(row["STATUSR"], row["FULLNAME"], row["WORKCENTER"],row["DRAWNUM"],row["STEXT"],0)
        # columns = [{"name": i, "id": i} for i in df_details.columns]
        # data = df_details.to_dict("records")
            style = {"border": "1px solid black","display": "flex", "justify-content": "space-between", "align-items": "center", "margin_top": "100"}


        else:
            fig = {}
            style = {"display": "none"}

        list_of_figs.append(fig)
        list_of_styles.append(style)

    return tuple(list_of_figs + list_of_styles)