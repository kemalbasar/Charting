# Import required libraries and modules
from datetime import datetime, date, timedelta
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.express as px
from decimal import Decimal
import plotly.graph_objs as go
from _plotly_utils.colors.qualitative import Alphabet
from dash import dcc, html, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from config import valftoreeg, project_directory
from run.agent import ag
from valfapp.app import app, cache
from valfapp.configuration import layout_color
from valfapp.layouts import nav_bar

questions = list(ag.run_query(r"SELECT DISTINCT  NAME1 FROM IASMATCUSTOMERS")["NAME1"])

# WHERE CUSTOMER = '10000030'

layout = [
    dcc.Store(id='generated_data2',data= {}), dcc.Download(id="download-energy2"), dcc.Download(id="download-energy3"),
    dcc.Store(id='shared-state'),

    # Navigation Bar
    nav_bar,

    # Energy Search and Filter Components
    
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        dcc.Input(
                            id='material', type='text', value=''
                        )], style={"margin-top": 18}), width=1),
            dbc.Col(
                html.Div(
                    [html.Datalist(
                        id='datalist-questions',
                        children=[html.Option(value=question) for question in questions]
                    ),

                        dcc.Input(id='customer',
                                  type='text',
                                  list='datalist-questions',
                                  value='',
                                  placeholder='',
                                  style={'width': '100%'}
                                  )], style={"margin-top": 18}), width=1),
            dbc.Col(
                html.Div(
                    [dcc.Dropdown(
                        id='date-dropdown2',
                        options=[
                            {'label': i, 'value': i}
                            for i in ['Day', 'Month']
                        ],
                        style={
                            'color': 'white',
                            'font': {'color': '#2149b4'},
                            'width': 220,
                        },
                        value='month',
                    ),
                    ],
                    style={"margin-top": 18},
                ),
                className="", width=1
            ),
            dbc.Col(
                html.Div(
                    [
                        dcc.DatePickerRange(
                            id='date-picker2',
                            className="dash-date-picker-multi",
                            start_date=(date.today() - timedelta(weeks=50)).isoformat(),
                            end_date=(date.today()).isoformat(),
                            display_format='YYYY-MM-DD',
                            style={'color': '#212121'},
                            persistence=True,
                            persistence_type='session',
                        ),
                        html.Button(
                            'Search',
                            id='search2',
                            className="dash-empty-button",
                            n_clicks=0,
                        ),
                        html.Button(
                            'Download',
                            id='download2',
                            className="dash-empty-button",
                            n_clicks=0,
                        ),
                        html.Button(
                            'DownloadF',
                            id='download3',
                            className="dash-empty-button",
                            n_clicks=0,
                        ),
                    ],
                ), style={"margin-left": 100, "margin-top": 15}
            ),
        ], style={"margin-top": 40, 'border': '3px dashed blue', "margin-left": 60}, className="g-0"
    ),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dash_table.DataTable(
                    id="data_table2",

                    data=[],
                    columns=[],
                    filter_action='native',
                    style_cell={
                        "textAlign": "center",
                        "padding": "10px",
                        "color": "black",
                        'max-width': 100
                    },
                    row_selectable='single',  # Enable multi-row selection
                    selected_rows=[],
                    style_table={
                        'borderCollapse': 'collapse',
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    sort_action='native'
                ),
                dbc.Button(id="unselect-rows-btn",
                            className="dash-empty-button",
                                style= {"margin-top":50}),
                dash_table.DataTable(
                    id="data_table3",
                    data=[],
                    columns=[],
                    filter_action='native',
                    style_cell={
                        "textAlign": "center",
                        "padding": "10px",
                        "color": "black",
                        'max-width': 100
                    },
                    style_table={
                        'borderCollapse': 'collapse',
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    sort_action='native'
                )

            ], style={"margin-top": 0}, className="")
        ], width=12, style={"margin-left": "100px"}), ],style={"margin-left":30,"margin-top":25})
]


# Define the callback to update the second dropdown
@cache.memoize()
def main_table(input_material, input_customer, s_date, f_date):
    if input_material == '' and input_customer == '':
        df = ag.run_query(f"EXEC VLFPRDENERGYPROC @WORKSTART=?, @WORKEND=?,@PROVIDEDMAT =?, @CUSTOMER =?",
                          params=[str(s_date), str(f_date), 0, f''])
    else:
        if input_material != '':

            df = ag.run_query(f"EXEC VLFPRDENERGYPROC @WORKSTART=?, @WORKEND=?,@PROVIDEDMAT =?, @CUSTOMER =?",
                              params=[str(s_date), str(f_date), 2, f'{input_material}'])
        else:

            df = ag.run_query(f"EXEC VLFPRDENERGYPROC @WORKSTART=?, @WORKEND=?,@PROVIDEDMAT =?, @CUSTOMER =?",
                              params=[str(s_date), str(f_date), 1, input_customer])



    df["TOTWEIGHT"] = df["TOTWEIGHT"].fillna(0)
    df["KWHPERTON"] = df.apply(lambda x: (x["TOTKWH"] / x["TOTWEIGHT"]) if x["TOTWEIGHT"] != 0 else 1.111, axis=1)
    df['KWHPERTON'] = df['KWHPERTON'].apply(lambda x: Decimal(x).quantize(Decimal('0.000')))
    costcenter_list = list(df["COSTCENTER"].unique())
    costcenter_list = [x.replace(' ', '') for x in costcenter_list]
    costcenter_list.insert(0, 'MATERIAL')
    pivot_table = df.pivot_table(index="MATERIAL", columns='COSTCENTER', values='KWHPERTON', aggfunc='first')
    pivot_table.reset_index(inplace=True)

    pivot_table.columns = [col.replace(' ', '') for col in pivot_table.columns]

    if input_material == '' and input_material == '':
        pivot_table = pivot_table[costcenter_list]
    else:
        pivot_table["PAKET"] = 0.000
        df_columns = ag.run_query(query=r"EXEC VLFPRDENERGYROTACHECK @MATERIAL=?", params=[input_material])
        columns_to_convert = [col for col in pivot_table.columns if col not in ['MATERIAL', 'TOTAL']]
        pivot_table[columns_to_convert] = pivot_table[columns_to_convert].apply(pd.to_numeric, errors='coerce')
        for col in list(df_columns["COSTCENTER"].unique()):
            if col not in pivot_table.columns:
                pivot_table[col] = 0.000
            else:
                pivot_table[col] = pivot_table[col].astype(float)
        pivot_table['TOTAL'] = pivot_table[
            [x for x in list(pivot_table.columns) if x not in ['MATERIAL', 'TOTAL']]].sum(axis=1, skipna=True)

    pivot_table_store = pivot_table.to_json(date_format='iso', orient='split')
    columns = [{"name": i, "id": i} for i in pivot_table.columns]
    return pivot_table, columns, pivot_table_store


@app.callback(
    Output("data_table2", "data"),
    Output("data_table2", "columns"),
    Output('generated_data2', 'data'),
    [State('date-picker2', 'start_date'),
     State('date-picker2', 'end_date'),
     State('material', 'value'),
     State('customer', 'value'),
     Input('search2', 'n_clicks')]
)
def cache_to_result(s_date, f_date, input_material, input_customer, button):
    if button <= 0:
        raise PreventUpdate

    pivot_table, columns, pivot_table_store = main_table(input_material, input_customer, s_date, f_date)

    return pivot_table.to_dict("records"), columns, pivot_table_store


# Assuming pivot_table is your DataFrame with the specified columns
# Listing the columns you want to sum

# Calculate the sum of the specified columns for each row

# If you want to treat rows with all NaN values in the specified columns as 0 instead of NaN in the total
# you can fill NaN values in the 'TOTAL' column with 0
# pivot_table['TOTAL'] = pivot_table['TOTAL'].fillna(0)


'''
    def query_result(column_name, material):
        # Placeholder for your actual query logic
        # This function now simulates a database query
        df1 = ag.run_query(
            f"SELECT B.ANAMAMUL, A.COSTCENTER FROM VLFALTPARCA B INNER JOIN IASROUOPR A ON A.MATERIAL = B.MATERIAL WHERE B.ANAMAMUL = '{material}' AND A.COSTCENTER = '{column_name}'")
        df2 = ag.run_query(
            f"SELECT DISTINCT COSTCENTER FROM IASROUOPR WHERE MATERIAL = '{material}' AND COSTCENTER = '{column_name}'")
        if df1.empty and df2.empty:
            return 'x'
        else:
            return '0'

    # Check for NaN and apply query_result function only if necessary
    def fill_if_nan(column_name, material_column):
        # Apply only to NaN values
        def apply_query(value):
            if pd.isna(value):
                return query_result(column_name, material_column)
            else:
                return value

        return apply_query

    # Apply the optimized function
    for column in pivot_table.columns:
        if column != 'MATERIAL':  # Skipping the 'Material' column itself
            material_column = pivot_table['MATERIAL']
            # Create a mask for NaN values in the current column
            nan_mask = pivot_table[column].isna()
            # Apply query_result only for NaN values
            pivot_table.loc[nan_mask, column] = pivot_table.loc[nan_mask].apply(
                lambda row: fill_if_nan(column, row['MATERIAL'])(row[column]), axis=1)
'''


@app.callback(
    Output('data_table2', 'style_data_conditional'),
    Output('data_table2' ,'style_table'),
    Output('data_table3', 'style'),
    Output("data_table3", "data"),
    Output("data_table3", "columns"),
    Input('shared-state', 'data'),
    Input('data_table2', 'selected_rows'),
    State('date-picker2', 'start_date'),
    State('date-picker2', 'end_date'),
    State('generated_data2', 'data'),
)
def update_style(go,selected_rows, s_date, f_date, pivot_table):

    print("here")
    try:
        df = pd.read_json(pivot_table, orient='split')
    except ValueError as e:
        df = pd.DataFrame(pivot_table)

    if not selected_rows:
        # If no rows are selected, don't apply any conditional style
        print("not selected")
        style = [
            # {
            #     'if': {'row_index': i},
            #     'display': 'table-row'  # Explicitly show the row, though this is typically not necessary
            # } for i in range(len(df))
        ]
        table_height = f"{30 * len(df) + 30}px"
        style2 = {'display': 'none'}
        style_table = {'height': table_height, 'borderCollapse': 'collapse'}
        return style, style_table, style2, pd.DataFrame().to_dict(
            "records"), []
    else:
        print("selected")
        df_details = ag.run_query(
            f"SELECT DISTINCT A.MPOINT,A.WORKCENTER,A.QTY,A.QTY*M.NETWEIGHT/1000 AS KG,A.KWH,CASE WHEN A.WORKINGHOUR = 0 THEN NULL ELSE A.IDEALCYCLETIME/A.WORKINGHOUR END AS PERFORMANCE,WORKSTART,WORKEND,A.SETUPTIME"
            f" FROM VLFPRDENERGY A LEFT JOIN IASMATBASIC M ON M.MATERIAL = A.MATERIAL"
            f" WHERE A.MATERIAL = '{df['MATERIAL'][selected_rows[0]]}' AND WORKSTART > '{s_date}' AND WORKEND < '{f_date}'")
        print(df_details)
        columns3 = [] if df_details is None else [{"name": i, "id": i} for i in df_details.columns]
        style = [
            {
                'if': {'row_index': i},
                'display': 'none'  # This will hide the row
            } for i in range(len(df)) if i not in selected_rows
        ]
        style2 = {'display': 'none'}

        visible_rows = len(df) - len(selected_rows)
        table_height = 180
        style_table = {'height': table_height, 'borderCollapse': 'collapse'}

        return style, style_table, style2, pd.DataFrame() if df_details is None else df_details.to_dict(
            "records"), columns3




@app.callback(
    Output('data_table2', 'selected_rows'),
    Input('unselect-rows-btn', 'n_clicks'),
    prevent_initial_call=True  # Prevents the callback from being triggered upon the initial load of the app
)
def unselect_rows(n_clicks):
    return []  # Returns an empty list to unselect all rows

@app.callback(
    Output("download-energy2", "data"),
    Input("download2", "n_clicks"),
    prevent_initial_call=True
)
def generate_excel(n_clicks, ):
    generated_data = ag.run_query(r"SELECT * FROM VLFPRDENERGY")
    if n_clicks < 1:
        raise PreventUpdate

    return dcc.send_data_frame(generated_data.to_excel, "energydata.xlsx", index=False) \
 \
        @ app.callback(
            Output("download-energy3", "data"),
            State(component_id='generated_data2', component_property='data'),
            Input("download3", "n_clicks"),
        )


def generate_excel2(generated_data, n_clicks, ):
    if n_clicks < 1:
        raise PreventUpdate
    generated_data = pd.read_json(generated_data, orient='split')

    return dcc.send_data_frame(generated_data.to_excel, "energydata.xlsx", index=False)
