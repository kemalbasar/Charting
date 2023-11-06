# Import required libraries and modules
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
    html.Div([
    dcc.Dropdown(
        id='machine-type-dropdown',
        options=[{'label': k, 'value': k} for k in valftoreeg.keys()],
        value=list(valftoreeg.keys())[0]  # Set the default value to the first key
    ),
    dcc.Dropdown(
        id='machine-dropdown',
    ),
    dcc.DatePickerRange(
            id='date-picker',
            start_date='2023-10-03',
            end_date='2023-10-05',
            display_format='YYYY-MM-DD',
        ),
    html.Button('search',id='search',n_clicks=0)
])
,
html.Br(),
html.Br(),
dash_table.DataTable(
                    id="data_table",
                    data = [],
                    columns= [],
                    style_cell={
                        "minWidth": "100px",
                        "width": "100px",
                        "maxWidth": "400px",
                        "textAlign": "center",
                    },
                )
    ]


# Define the callback to update the second dropdown
@app.callback(
    Output('machine-dropdown', 'options'),
    Input('machine-type-dropdown', 'value')
)
def set_machine_options(selected_machine_type):
    return [{'label': k, 'value': v} for k, v in valftoreeg[selected_machine_type].items()]




@app.callback(
    Output("data_table", "data"),
    Output("data_table", "columns"),
    [State('date-picker', 'start_date'),
     State('date-picker', 'end_date'),
     State('machine-type-dropdown', 'value'),
     State('machine-dropdown', 'value'),
     Input('search','n_clicks')]
)
def update_table(s_date,f_date,costcenter,m_point,button):
    print("buraruauru")
    if button <= 0:
        raise PreventUpdate
    with open(f"F:\pycarhm projects\Charting\queries\energy_qandweight.sql", 'r') as file:
        filedata = file.read()
    print(s_date)
    print(f_date)
    start_date = datetime(datetime.now().year, datetime.now().month, 1)
    analyzer = valftoreeg[costcenter][m_point]
    for item in valftoreeg:
        for i in range(3):
            finish_date = start_date + relativedelta(months=+1)

            filedata = filedata.replace("xxxx-yy-zz",start_date)
            filedata = filedata.replace("aaaa-bb-cc",finish_date)
            filedata = filedata.replace("XXMATERIALYY",item)
            print("************")
            print(filedata)
            df_works = ag.run_query(filedata)
            print("************")
            print(df_works)
            df_works["CONSUMPTION (kwh)"] = 0.00

            code_wc = valftoreeg[item]
            code_works = start_date.strftime('%Y-%m-%dT%H:%M:%S')
            code_worke = finish_date.strftime('%Y-%m-%dT%H:%M:%S')

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
                    "point": [code_wc],
                    "start": code_works,
                    "end": code_worke,
                    "break": {
                        "type": "point"
                    },
                    "resolution": "month"
                }
            }

            # Make the POST request
            response = requests.post(url, data=json.dumps(payload), headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                # print(json.dumps(response_data, indent=4))  # Pretty print the JSON response
            else:
                print(f"HTTP Error: {response.status_code}")

            g_total = 0.00
            if response_data["properties"]["data"]['0'] is not None:
                for item in response_data["properties"]["data"]['0']:
                    g_total = g_total + (item[2])
                df_works["CONSUMPTION (kwh)"][i] = g_total

            df_final = pd.concat([df_works, df_final]).drop_duplicates().reset_index(drop=True)
    df_final.sort_values(by="CONSUMPTION (kwh)", ascending=False, inplace=True)
    columns = [{"name": i, "id": i} for i in df_final.columns]
    return df_final.to_dict("records"),columns
