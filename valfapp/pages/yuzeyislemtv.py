from datetime import date, timedelta, datetime
from valfapp.app import workcenters, app, prdconf, return_piechart
import dash_table
import json
import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import indicator_for_tvs, indicator_for_yislem
from valfapp.app import app
from config import project_directory
from run.agent import ag

len_fig = int(len(ag.run_query(project_directory + r"\Charting\queries\yuzeyislemtvsorgu.sql")) / 8) + 1


def dynamic_layout(list_of_figs=[], col_num=5,row_num=3):
    total_chart = col_num*row_num
    widthof = int(12/col_num)
    lengthof = len(list_of_figs)
    x = lengthof % total_chart
    newlengthof = lengthof - x
    numofforths = newlengthof / total_chart
    counter = 0
    print(f'here is total chart{total_chart}')
    listofdivs = []
    for i in range(0, len(list_of_figs), total_chart):
        print(f"**{i}**")
        if counter < numofforths:
            listofdivs.append(html.Div(	[	dbc.Row(
				[ dbc.Col(html.Div(children=[dcc.Graph(figure=list_of_figs[i + k + col_num*l ])],style={'border': '2px solid black'}),width=widthof)
				for k in range(col_num) ],className = "g-0") for l in range(row_num)	] ) )
        else:
            if x == 0:
                continue
            else:
                all_rows = []

                # Loop over each row
                for l in range(row_num):
                    # Initialize an empty list for the columns of this row
                    row_columns = []

                    # Loop over each column
                    for k in range(col_num):

                        # Calculate the index for the figure
                        fig_index = i + k +  l*col_num
                        print("herasdasdasdasfdsdafsdfe")

                        print(fig_index)
                        print("herasdasdasdasfdsdafsdfe")

                        if fig_index%total_chart < x:
                            column = dbc.Col(html.Div(children=[dcc.Graph(figure=list_of_figs[fig_index])],
                                                      style={'border': '2px solid black'}),
                                             width=widthof)
                        else:

                        # Create the column with the Graph and its style
                            column = dbc.Col(html.Div(children=[dcc.Graph(figure={"data": [],  # No data since it's an empty figure
                            "layout":{ "width": 1450/col_num, "height": 850/row_num}})],
                                                      style={'border': '2px solid black'}),
                                             width=widthof)

                        # Add the column to the list of columns
                        row_columns.append(column)

                    # Create a dbc.Row with the columns and no gutters, then add to the list of rows
                    row = dbc.Row(row_columns, className="g-0")
                    all_rows.append(row)


            listofdivs.append(all_rows)



        counter = counter + 1

    print("*************")
    print(listofdivs)
    print("*************")

    return listofdivs


def update_ind_fig(col_num,row_num):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_stationss (list): The list of work centers to display.

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.
    """
    df = ag.run_query(project_directory + r"\Charting\queries\yuzeyislemtvsorgu.sql")

    list_of_figs = []
    list_of_stationss = []
    for item in df.loc[df["COSTCENTER"] != "YUZEYIsSLEM"]["WORKCENTER"].unique():
        list_of_stationss.append(item)
    for index, row in df.iterrows():
        if index < len(list_of_stationss):
            fig = indicator_for_yislem(row["STATUSR"], row["FULLNAME"], row["WORKCENTER"], row["DRAWNUM"],
                                       row["STEXT"], row["TARGET"],{"width": 1500/col_num if  col_num <= 4 else 1250/col_num, "height": 850/row_num},8/(row_num*col_num))

            list_of_figs.append(fig)

        else:
            fig = {}
            style = {"display": "none"}

    return dynamic_layout(list_of_figs, col_num,row_num)



layout = [dcc.Link(
    children='Main Page',
    href='/',
    style={"height": 40, "color": "black", "font-weight": "bold"}

),
    dcc.Store(id="list_of_stationss"),
    # dcc.Store(id="wc-output-container_yislem_tmp", data=update_ind_fig(2,4)),
    dcc.Store(id="update_flag"),
    dcc.Store(id="livedata_yislem", data=ag.run_query(project_directory +
                                                      r"\Charting\queries\yuzeyislemtvsorgu.sql").to_json(
        date_format='iso', orient='split')),
    dcc.Store(id="wc-output-container_yislem_tmp",data=update_ind_fig(5,3)),
    dcc.Interval(id="animate_yislem", interval=10000),
    dbc.Col([
        dbc.Row([html.Div(id="wc-output-container_yislem_real", className="g-0"), ]),
        dbc.Row([
            html.Button("Play", id="play_yi", style={'width': '50px'}),
            dcc.Slider(
                min=0,
                max=len_fig,
                step=1,
                value=-1,
                id='wc-slider_yislem',
                className='slider'
            ), dcc.Input(
                    id="inp_row",
                    placeholder="row",
                    value=3,
                    type = 'number',
                    style={"width": "180px"},
                    persistence=True,  # Enable persistence
                    persistence_type='local' # Store in local storage
                ),
                dcc.Input(
                    id="inp_col",
                    placeholder="col",
                    value=5,
                    type='number',
                    style={"width": "180px"},
                    persistence=True,  # Enable persistence
                    persistence_type='local'  # Store in local storage
                ),
               html.Button("Proceed",n_clicks=0, id="proceed_but", style={'width': '50px'})
        ], className="g-0"),

    ], width=12,style= {"margin-left":100}),
]



@app.callback(
    Output("animate_yislem", "disabled"),
    Input("play_yi", "n_clicks"),
    State("animate_yislem", "disabled"),
)
def toggle(n, playing):

    if n:
        return not playing
    return playing


@app.callback(
    Output("wc-output-container_yislem_real", "children"),
    Output("wc-slider_yislem", "value"),
    Output('wc-output-container_yislem_tmp', 'data'),
    Input('animate_yislem', 'n_intervals'),
    State("inp_col", "value"),
    State("inp_row", "value"),
    Input("wc-slider_yislem", "value"),
    Input("proceed_but", "n_clicks"),
    State('wc-output-container_yislem_tmp', 'data'),
)
def show_div(n,col,row,k, changelayout,listofdivs):
    if changelayout:
        listofdivs = update_ind_fig(col,row)
    if listofdivs is None:
        listofdivs = update_ind_fig(col,row)



    if k >= len(listofdivs):
        return listofdivs[0], 0,update_ind_fig(col,row)
    else:
        return listofdivs[k], k + 1,listofdivs

# @app.callback(
#     Output("wc-output-container_yislem_real", "children"),
#     Input("play", "n_clicks"),
#     State("inp_col", "value"),
#     State("inp_row", "value"),
# )
# def show_div(proceed_but,col,row):
#     return update_ind_fig(col,row)
