# Import required libraries and modules
import math
from datetime import datetime

import plotly.express as px
import plotly.graph_objs as go

from dash import dcc, html, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from valfapp.app import cache, oee, app
import requests
import json
from config import reengen_company,reengen_password,reengen_username,valftoreeg,project_directory
from run.agent import ag,agiot
from dateutil.relativedelta import relativedelta
import pandas as pd
import dash_bootstrap_components as dbc
import dash_table



# # API Endpoint
# url = "https://api.reengen.com/api/do/"
#
#
# # Authentication payload
# auth_payload = {
#     "$": "Authenticate",
#     "properties": {
#         "tenant": reengen_company,  # Replace with your tenant name
#         "user": reengen_username ,      # Replace with your username
#         "password": reengen_password  # Replace with your password
#     }
# }
#
# headers = {
#     'Content-Type': 'application/json'
# }
#
# # Make the POST request for auth
# response = requests.post(url, data=json.dumps(auth_payload), headers=headers)
#
# # Check if the request was successful
# if response.status_code == 200:
#     response_data = response.json()
#     if response_data["succeeded"]:
#         connection_id = response_data["properties"]["connectionId"]
#         print(f"Connection ID: {connection_id}")
#     else:
#         print(f"Authentication failed: {response_data['message']}")
# else:
#     print(f"HTTP Error: {response.status_code}")
#

query = f"SELECT MPOINT, SUBSTRING(DATE, 1, 8) AS DATE, SUM(OUTPUT) AS TOTAL FROM VLFENERGY WHERE COSTCENTER = 'TRAFO' GROUP BY MPOINT, SUBSTRING(DATE, 1, 8)"

df = ag.run_query(query)
fig = px.bar(df, x='DATE', y='TOTAL', width=600, height=400)
fig.update_layout(bargap=0.2)
# Adjust space between bars (e.g., 0.05 for 5% gap)
layout = [
    dbc.Row(html.H1("Valfsan Production Energy Consumption",
                    style={'text-align': 'center', "textfont": 'Arial Black'})),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dcc.Link(
                    children='Main Page',
                    href='/',
                    style={"color": "black", "font-weight": "bold"}
                ),
                html.Br(),
                html.Div(
                    [
                        # Div for dropdowns and date pickers
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id='machine-type-dropdown',
                                    options=[{'label': k, 'value': k} for k in valftoreeg.keys()],
                                    value=list(valftoreeg.keys())[0]  # Set the default value to the first key
                                ),
                                dcc.Dropdown(
                                    id='machine-dropdown'
                                ),
                                dcc.DatePickerRange(
                                    id='date-picker',
                                    className="dash-date-picker-multi",
                                    start_date='2023-10-03',
                                    end_date='2023-10-05',
                                    display_format='YYYY-MM'
                                )
                            ],
                            style={'display': 'inline-block', 'width': 'auto', 'margin-right': '20px'}
                        ),
                        # Separate Div for the button
                        html.Div(
                            [
                                html.Button(
                                    'Search',
                                    id='search',
                                    className="dash-empty-button",
                                    n_clicks=0
                                )
                            ],
                            style={'display': 'inline-block', 'text-align': 'center'}
                        )
                    ],

                )]),
            dbc.Row([
                    dash_table.DataTable(
                        id="data_table",
                        data = [],
                        columns= [],
                        style_cell={
                            "minWidth": "100px",
                            "width": "100px",
                            "maxWidth": "150px",
                            "textAlign": "center",
                        },
                        style_table={
                            'width': 100,  # Table width to match the parent container
                            'margin': 'left',  # Center the table within the parent container
                            'borderCollapse': 'collapse',  # Optional: for collapsing cell borders
                        },
                        sort_action='native',
                        )

            ],style={"margin-top": 50}
)
    ]),
        dbc.Col([dcc.Graph(
            id='example-graph',
            figure=fig
        ),
            dcc.Graph(id="line_chart_combined") ]
            , width=4)
    ]),
    dbc.Row([
        dbc.Col(),


    ])
]

# Define the callback to update the second dropdown
@app.callback(
    Output('machine-dropdown', 'options'),
    Input('machine-type-dropdown', 'value')
)
def set_machine_options(selected_machine_type):
    return [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]



@cache.memoize()
def update_table(begin_month,begin_year,final_month,final_year,costcenter,m_point):
    selected_point = m_point
    with open(project_directory + f"\Charting\queries\energy_qandweight.sql", 'r') as file:
        filedata = file.read()
    start_date = datetime(begin_year, begin_month, 1)
    end_date  = datetime(final_year, final_month, 1)
    code_works = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    code_worke = end_date.strftime('%Y-%m-%dT%H:%M:%S')

    difference = relativedelta(end_date, start_date)
    # Extract the number of months and years in the difference
    month_difference = difference.months + difference.years * 12

    df_final = pd.DataFrame()
    analizorler = []
    if costcenter != 'Bütün':
        analyzer = valftoreeg[costcenter]
        analizorler.append((m_point,costcenter))
    else:
        analyzer = {}
        for costcenter_tmp in valftoreeg:
            analyzer.update(valftoreeg[costcenter_tmp])
            for item in valftoreeg[costcenter_tmp]:
                analizorler.append((item,costcenter_tmp))
    print(analizorler)
    for m_point in analizorler:

        costcenter_tmp = m_point[1]
        m_point = m_point[0]

        if m_point == 'Bölümler' or m_point == 'Analizörler':
            continue


        if m_point == "K-13','K-18','K-19','K-20','K-21','K-22','K-23','K-25','K-27','K-28":
            m_point_tmp = '10 Kurutma'
        elif m_point == "T-19','T-20','T-21','T-22','T-23','T-24','T-25','T-26','T-27','T-34','T-37','T-43','T-44','T-45":
            m_point_tmp = '10 Tambur'
        elif m_point == "CNCTO-01','CNCTO-02','CNCTO-04','CNCTO-05','CNCTO-06','CNC-TO-07','CNCTO-08','CNCTO-09','CNCTO-10','CNCTO-11','CNCTO-12','CNCTO-13','CNCTO-14','CNC-TO-15','CNCTO-16','CNC-07','CNC-08','CNC-26','CNC-28":
            m_point_tmp = "19 CNC (Pano 1)"
        elif m_point == "CNCTO-01','CNCTO-02','CNCTO-04','CNCTO-05','CNCTO-06','CNCTO-07','CNCTO-08','CNCTO-09','CNCTO-10','CNCTO-11','CNCTO-12','CNCTO-13','CNCTO-14','CNCTO-15','CNCTO-16','CNC-07','CNC-08','CNC-26','CNC-28":
            m_point_tmp = "19 CNC (Pano 1)"
        elif m_point == "CNC-04', 'CNC-11', 'CNC-13', 'CNC-14', 'CNC-15', 'CNC-16', 'CNC-17', 'CNC-18', 'CNC-19', 'CNC-20', 'CNC-21', 'CNC-22', 'CNC-23', 'CNC-29', 'Z-01":
            m_point_tmp = "15 CNC (Pano 2)"
        elif m_point == "CNC-01', 'CNC-03', 'CNC-06', 'CNC-12', 'CNC-24', 'TB-01', 'STASLAMA', 'HONLAMA', 'ZIMPARA":
            m_point_tmp = "5 CNC ve 4 Taslama (Pano 3)"
        elif m_point == "P-04', 'P-08', 'P-24', 'P-36', 'P-46', 'P-50', 'P-69', 'P-76":
            m_point_tmp = "8 Pres (Salter 2)"
        elif m_point == "P-11', 'P-47', 'P-62', 'P-74":
            m_point_tmp = "4 Pres (Salter 3)"
        elif m_point == "P-12', 'P-19', 'P-23', 'P-30', 'P-31', 'P-33', 'P-34', 'P-37', 'P-55', 'P-56', 'P-61', 'P-70', 'P-71":
            m_point_tmp = "13 Pres (Salter 5)"
        elif m_point == "P-14', 'P-26', 'P-64', 'P-67', 'P-68', 'P-75', 'P-63', 'P-65', 'P-73', 'TC-05":
            m_point_tmp = "10 Pres (Salter 4-6)"
        else:
            m_point_tmp = m_point


        df_works = ag.run_query(f"SELECT LEFT(DATE, 4) + '-' + SUBSTRING(DATE, 6, 2)  AS DATE,MPOINT,SCODE,"
                                f"SUM(OUTPUT) AS OUTPUT,COSTCENTER,INTERVAL FROM VLFENERGY"
                                f" WHERE MPOINT = '{m_point_tmp}' AND  DATE BETWEEN '{code_works}' AND '{code_worke}'"
                                f"GROUP BY LEFT(DATE, 4) + '-' + SUBSTRING(DATE, 6, 2),MPOINT,SCODE,COSTCENTER,INTERVAL")
        print(df_works)
        print("******")

        if len(df_works) == 0:
            continue

        filedata_tmp = filedata.replace("xxxx-yy-zz",str(start_date))
        filedata_tmp = filedata_tmp.replace("aaaa-bb-cc",str(end_date))
        try:
            filedata_tmp = filedata_tmp.replace("XXMATERIALYY","'"+m_point+"'")
        except (TypeError) as e:
            filedata_tmp = filedata_tmp.replace("XXMATERIALYY","x")

        #manüpüle ettiğimiz sorguyu çalıştırıyoruz ve yeni bir sütun ekliyoruz.
        df_prddata = ag.run_query(filedata_tmp)
        df_prddata["MPOINT"] = m_point_tmp

        if len(df_prddata):
            df_works = df_works.merge(df_prddata, on=['MPOINT','DATE'], how='left').fillna(0)
            print(f"{df_works}")
            print(f"***********")

        else:
            df_prddata["MPOINT"] = m_point
            df_prddata["QUANTITY"] = 0
            df_prddata["TOTALWEIGHT"] = 0
            df_prddata["kwhkg"] = 0.00


        df_final = pd.concat([df_works, df_final]).drop_duplicates().reset_index(drop=True)
    df_final["kwhkg"]=df_final["kwhkg"].astype(float)
    df_final["TOTALWEIGHT"]=df_final["TOTALWEIGHT"].astype(float)
    df_final["OUTPUT"]=df_final["OUTPUT"].astype(float)
    print(df_final.dtypes)
    df_final["kwhkg"] = df_final.apply(lambda x: x["OUTPUT"] / x["TOTALWEIGHT"] if x["TOTALWEIGHT"] > 0 else 0,axis=1)
    df_final["kwhqty"] = df_final.apply(lambda x: x["OUTPUT"] / x["QUANTITY"] if x["QUANTITY"] > 0 else 0,axis=1)
    df_final["kwhkg"] = df_final["kwhkg"]*1000
    df_final["kwhkg"] = df_final["kwhkg"].apply(lambda x: f"{x:.1f}")
    df_final["kwhqty"] = df_final["kwhqty"].apply(lambda x: f"{x:.2f}")
    df_final['DATE'] = df_final['DATE'].apply(lambda x: datetime.strptime(x, '%Y-%m'))

    print(df_final['DATE'].dtypes)

    # print(selected_point)
    # if selected_point == 'Bölümler':
    #     mask = ((df_final['COSTCENTER'] == 'CNC') | (df_final['COSTCENTER'] == 'PRESHANE')) & (
    #         ~df_final['ANALYZER'].str.contains('pano', na=False))
    #     df_final.loc[mask, ['CONSUMPTION', 'QUANTITY']] = 0
    #     df_final = df_final.groupby(["COSTCENTER","DATE"]).agg({"TOTALWEIGHT": "sum","kwhkg": "mean","CONSUMPTION": "sum","QUANTITY":"sum",})
    #     df_final.reset_index(inplace=True)

    df_final.sort_values(by="kwhkg", ascending=False, inplace=True)
    print(df_final)
    return df_final.to_json(date_format='iso', orient='split')




@app.callback(
    Output("data_table", "data"),
    Output("data_table", "columns"),
    [State('date-picker', 'start_date'),
     State('date-picker', 'end_date'),
     State('machine-type-dropdown', 'value'),
     State('machine-dropdown', 'value'),
     Input('search','n_clicks')]
)
def cache_to_result(s_date,f_date,costcenter,m_point,button):
    if button <= 0:
        raise PreventUpdate
    f_date = datetime.strptime(f_date, "%Y-%m-%d")
    f_date = str(f_date + relativedelta(months=+1))
    final_month = int(f_date[5:7])
    begin_month = int(s_date[5:7])
    final_year = int(s_date[0:4])
    begin_year = int(s_date[0:4])
    df_final = update_table(begin_month,begin_year,
                            final_month , final_year,costcenter,m_point)
    df_final = pd.read_json(df_final, orient='split')
    columns = [{"name": i, "id": i} for i in df_final.columns]
    return df_final.to_dict("records"),columns



@app.callback(
    Output("line_chart_combined", "figure"),
    [Input("data_table", "data")]
)
def line_graph_update(data):
    # Convert the input data to a DataFrame
    print("here")
    df = pd.DataFrame(data)
    df.sort_values(by="DATE", ascending=False, inplace=True)
    fig_combined = go.Figure()

    # Add trace for kwhkg

    fig_combined.add_trace(go.Scatter(x=df["DATE"], y=df["kwhkg"], mode='lines+markers', name='kWh/kg'))

    # Add trace for kwhqty
    fig_combined.add_trace(go.Scatter(x=df["DATE"], y=df["kwhqty"], mode='lines+markers', name='kWh/Quantity'))

    # Update layout
    fig_combined.update_layout(
        title='Energy Consumption Comparison',
        xaxis_title='Date',
        yaxis_title='Energy Consumption',
        legend_title="Metrics"
    )

    return fig_combined