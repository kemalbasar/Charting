# Import required libraries and modules
import math
from datetime import datetime
from dash import dcc, html, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from valfapp.app import cache, oee, app
import dash_table
import requests
import json
from config import reengen_company,reengen_password,reengen_username,valftoreeg
from run.agent import ag
from dateutil.relativedelta import relativedelta
import pandas as pd
import dash_bootstrap_components as dbc

pd.set_option("display.precision", 2)


# API Endpoint
url = "https://api.reengen.com/api/do/"


# Authentication payload
auth_payload = {
    "$": "Authenticate",
    "properties": {
        "tenant": reengen_company,  # Replace with your tenant name
        "user": reengen_username ,      # Replace with your username
        "password": reengen_password  # Replace with your password
    }
}

headers = {
    'Content-Type': 'application/json'
}

# Make the POST request for auth
response = requests.post(url, data=json.dumps(auth_payload), headers=headers)

# Check if the request was successful
if response.status_code == 200:
    response_data = response.json()
    if response_data["succeeded"]:
        connection_id = response_data["properties"]["connectionId"]
        print(f"Connection ID: {connection_id}")
    else:
        print(f"Authentication failed: {response_data['message']}")
else:
    print(f"HTTP Error: {response.status_code}")





layout = [
html.H1("Valfsan Production Energy Consumption", style={'text-align': 'center', "textfont": 'Arial Black'}),
dcc.Link(
        children='Main Page',
        href='/',
        style={"color": "black", "font-weight": "bold"}
    ),
html.Br(),
dbc.Col([
dbc.Row(html.Div(
    [
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
                    className = "dash-date-picker-multi",
                    start_date='2023-10-03',
                    end_date='2023-10-05',
                    display_format='YYYY-MM-DD'
                )
            ],
            style={'position': 'relative', 'display': 'inline-block', 'width': 'auto', 'margin-right': '20px'}
        ),
        html.Div(
            [
                html.Button(
                    'Search',
                    id='search',
                    className="dash-empty-button",
                    n_clicks=0
                )
            ],
            style={'position': 'relative', 'display': 'inline-block'}
        )
    ],
    style={ 'padding': '10px', 'width': '95%', 'display': 'flex', 'justify-content': 'space-between'}
),style={'width': 4})
,
dbc.Row(dash_table.DataTable(
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
                            'width': '40%',  # Table width to match the parent container
                            'margin': 'auto',  # Center the table within the parent container
                            'borderCollapse': 'collapse',  # Optional: for collapsing cell borders
                        },
                    ),style={'width': 4,"margin-top":50})
        ])]


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
    with open(f"F:\pycarhm projects\Charting\queries\energy_qandweight.sql", 'r') as file:
        filedata = file.read()
    start_date = datetime(begin_year, begin_month, 1)
    end_date  = datetime(final_year, final_month, 1)
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
        print(f"{m_point}hello000")
        for i in range(month_difference):
            filedata_tmp = filedata.replace("xxxx-yy-zz",str(start_date))
            filedata_tmp = filedata_tmp.replace("aaaa-bb-cc",str(end_date))
            try:
                filedata_tmp = filedata_tmp.replace("XXMATERIALYY","'"+m_point+"'")
            except (TypeError) as e:
                filedata_tmp = filedata_tmp.replace("XXMATERIALYY","x")

            #manüpüle ettiğimiz sorguyu çalıştırıyoruz ve yeni bir sütun ekliyoruz.
            df_works = ag.run_query(filedata_tmp)
            df_works["COSTCENTER"] = ''
            df_works = df_works[["ANALYZER","COSTCENTER","DATE","QUANTITY","TOTALWEIGHT","CONSUMPTION","kwhkg"]]
            code_works = start_date.strftime('%Y-%m-%dT%H:%M:%S')
            code_worke = end_date.strftime('%Y-%m-%dT%H:%M:%S')
            payload = {
                "$": "GetData",
                "properties": {
                    "series": [
                        {
                            "definition": "activeEnergy",
                            "variant": "import",
                            "type": "actual",
                            "xFunction": "sum",
                            "unit": "kWh",
                            "decimalPoints": 3
                        },
                    ],
                    "point": [analyzer[m_point]],
                    "start": code_works,
                    "end": code_worke,
                    "break": {
                        "type": "point"
                    },
                    "resolution": "day"
                }
            }
            print(payload)
            # Make the POST request
            response = requests.post(url, data=json.dumps(payload), headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
#                print(json.dumps(response_data, indent=4))  # Pretty print the JSON response
            else:
                print(f"HTTP Error: {response.status_code}")
            print(response_data)
            g_total = 0.00
            if m_point == "K-13','K-18','K-19','K-20','K-21','K-22','K-23','K-25','K-27','K-28":
                m_point = '10 Kurutma'
            elif m_point == "T-19','T-20','T-21','T-22','T-23','T-24','T-25','T-26','T-27','T-34','T-37','T-43','T-44','T-45":
                m_point = '10 Tambur'
            if response_data["properties"]["data"]['0'] is not None:
                for item in response_data["properties"]["data"]['0']:

                    g_total = g_total + (item[2])
                if len(df_works) > 0:
                    print(1)



                    df_works["ANALYZER"] = m_point
                    df_works["CONSUMPTION"][0] = round(g_total,2)
                    print(f"{costcenter_tmp}helllo")
                    df_works["COSTCENTER"][0] = costcenter_tmp
                else:
                    print(2)
                    df_works.loc[len(df_works.index)] = [m_point,costcenter_tmp,'2023-10', 0, 0,round(g_total,2),0]
            else:
                if df_works is None or len(df_works) <= 0:
                    print(3)
                    df_works.loc[len(df_works.index)] = [m_point,costcenter_tmp,'2023-10', 0, 0, round(g_total,2), 0]

                else:
                    df_works["ANALYZER"] = m_point
                    df_works["COSTCENTER"] = costcenter_tmp
                    print(4)
            df_final = pd.concat([df_works, df_final]).drop_duplicates().reset_index(drop=True)
            start_date = start_date + relativedelta(months=+1)
        start_date = datetime(begin_year, begin_month, 1)

    df_final.groupby(["ANALYZER"])["CONSUMPTION"].sum()
    df_final["kwhkg"] = df_final.apply(lambda x: x["CONSUMPTION"] / x["TOTALWEIGHT"] if x["TOTALWEIGHT"] != 0 else 0,axis=1)
    df_final["kwhkg"] = df_final["kwhkg"].apply(lambda x: f"{x:.2f}")
    print(selected_point)
    if selected_point == 'Bölümler':
        mask = ((df_final['COSTCENTER'] == 'CNC') | (df_final['COSTCENTER'] == 'PRESHANE')) & (
            ~df_final['ANALYZER'].str.contains('pano', na=False))
        df_final.loc[mask, ['CONSUMPTION', 'QUANTITY']] = 0
        df_final = df_final.groupby(["COSTCENTER","DATE"]).agg({"TOTALWEIGHT": "sum","kwhkg": "mean","CONSUMPTION": "sum","QUANTITY":"sum",})
        df_final.reset_index(inplace=True)

    df_final.sort_values(by="CONSUMPTION", ascending=False, inplace=True)
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

