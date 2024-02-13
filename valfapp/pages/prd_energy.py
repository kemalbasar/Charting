# Import required libraries and modules
from datetime import datetime, date, timedelta
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.express as px
from decimal import Decimal
import plotly.graph_objs as go
from _plotly_utils.colors.qualitative import Alphabet
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from config import valftoreeg, project_directory
from run.agent import ag
from valfapp.app import app
from valfapp.configuration import layout_color
from valfapp.layouts import nav_bar


layout = [
    # Your commented-out buttons
    # dbc.Button("Day", id="btn-day_en", n_clicks=0, color="primary", className='day-button'),
    # dbc.Button("Week", id="btn-week1_en", n_clicks=0, color="primary", className='week-button'),
    # dbc.Button("Month", id="btn-month1_en", n_clicks=0, color="primary", className='month-button'),
    # dbc.Button("Year", id="btn-year1_en", n_clicks=0, color="primary", className='year-button'),

    # Store and Download components
    dcc.Store(id='generated_data2'), dcc.Download(id="download-energy2"), dcc.Download(id="download-energy3"),

    # Navigation Bar
    nav_bar,

    # Energy Search and Filter Components

    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        dcc.Input(
                            id='text-input', type='text', value=''
                        )], style={"margin-top": 18}), width=1),
            dbc.Col(
                html.Div(
                    [dcc.Dropdown(
                        id='machine-dropdown2',
                        style={
                            'color': 'white',
                            'width': 220,
                        },
                        value='Analizörler'
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
                            start_date=(date.today() - timedelta(weeks=1)).isoformat(),
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
        ], style={"margin-top": 40, 'border': '3px dashed blue', "margin-left": 44}, className="g-0"
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
                ),

            ], style={"margin-top": 75}, className="")
        ], width=12, style={"margin-left": "100px"}),])
]


# Define the callback to update the second dropdown
@app.callback(
    Output('machine-dropdown2', 'options'),
    Input('machine-type-dropdown2', 'value')
)
def set_machine_options(selected_machine_type):
    if selected_machine_type in ["Bütün", "HAVALANDIRMA - FAN"]:
        return [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
    else:
        print("herehere")
        list_of_mpoints = [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
        list_of_mpoints.append({"label": "Hepsi", "value": "Hepsi"})
        print(list_of_mpoints)
        return list_of_mpoints




@app.callback(
    Output("data_table2", "data"),
    Output("data_table2", "columns"),
    Output("data_table3", "data"),
    Output("data_table3", "columns"),
    Output('generated_data2', 'data'),
    [State('date-picker2', 'start_date'),
     State('date-picker2', 'end_date'),
     State('text-input', 'value'),
     State('machine-dropdown2', 'value'),
     State('date-dropdown2', 'value'),
     Input('search2', 'n_clicks')]
)
def cache_to_result(s_date, f_date, input_material, m_point, date_interval, button):
    if button <= 0:
        raise PreventUpdate
    print("***")
    print(input_material)
    if input_material == 'Enter material...' or input_material == '':
        df = ag.run_query(f"SELECT * FROM VLFPRDENERGYVİEW")
    else:
        df = ag.run_query(f"SELECT * FROM VLFPRDENERGYVİEW WHERE MATERIAL = '{input_material}'")

    df["TOTWEIGHT"] = df["TOTWEIGHT"].fillna(0)
    df["KWHPERTON"] = df.apply(lambda x: (x["TOTKWH"] / x["TOTWEIGHT"]) if x["TOTWEIGHT"] != 0 else 1.111, axis=1)
    df['KWHPERTON'] = df['KWHPERTON'].apply(lambda x: Decimal(x).quantize(Decimal('0.000')))
    costcenter_list = list(df["COSTCENTER"].unique())
    costcenter_list = [x.replace(' ', '') for x in costcenter_list]
    costcenter_list.insert(0, 'MATERIAL')
    pivot_table = df.pivot_table(index="MATERIAL", columns='COSTCENTER', values='KWHPERTON', aggfunc='first')
    pivot_table.reset_index(inplace=True)

    pivot_table.columns = [col.replace(' ', '') for col in pivot_table.columns]
    df_details = pd.DataFrame(columns=["A","B","C"])

    if input_material == '' or input_material == '':
        print("here")

        pivot_table = pivot_table[costcenter_list]


    else:
        pivot_table["PAKET"] = 0.000
        df_columns = ag.run_query(query=r"EXEC VLFPRDENERGYROTACHECK @MATERIAL=?", params=[input_material])
        print("*********")
        print(pivot_table.columns)
        print("*********")
        columns_to_convert = [col for col in pivot_table.columns if col not in ['MATERIAL', 'TOTAL']]
        pivot_table[columns_to_convert] = pivot_table[columns_to_convert].apply(pd.to_numeric, errors='coerce')
        for col in list(df_columns["COSTCENTER"].unique()):
            if col not in pivot_table.columns:
                pivot_table[col] = 0.000
            else:
                pivot_table[col] = pivot_table[col].astype(float)
        print(df_columns["COSTCENTER"].unique())
        print(pivot_table[df_columns["COSTCENTER"].unique()].sum(axis=1, skipna=True))
        pivot_table['TOTAL'] = pivot_table[[x for x in list(pivot_table.columns) if x not in ['MATERIAL','TOTAL']]].sum(axis=1, skipna=True)
        df_details = ag.run_query(f"SELECT * FROM VLFPRDENERGYVİEW_DETAILS WHERE MATERIALREAL = '{input_material}'")

    print("******")
    print(pivot_table.dtypes)
    print([x for x in list(pivot_table.columns) if x != 'MATERIAL'])
    pivot_table_store = pivot_table.to_json(date_format='iso', orient='split')
    columns = [{"name": i, "id": i} for i in pivot_table.columns]
    columns3 = [{"name": i, "id": i} for i in df_details.columns]
    print("***")
    print(columns)
    return pivot_table.to_dict("records"),columns,df_details.to_dict("records"),columns3,pivot_table_store

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
    Output("download-energy2", "data"),
    Input("download2", "n_clicks"),
    prevent_initial_call=True
)
def generate_excel(n_clicks,):
    generated_data = ag.run_query(r"SELECT * FROM VLFPRDENERGY")
    if n_clicks < 1:
        raise PreventUpdate

    return dcc.send_data_frame(generated_data.to_excel, "energydata.xlsx", index=False)\

@app.callback(
    Output("download-energy3", "data"),
    State(component_id='generated_data2', component_property='data'),
    Input("download3", "n_clicks"),
)
def generate_excel2(generated_data,n_clicks,):

    if n_clicks < 1:
        raise PreventUpdate
    generated_data = pd.read_json(generated_data, orient='split')

    return dcc.send_data_frame(generated_data.to_excel, "energydata.xlsx", index=False)
