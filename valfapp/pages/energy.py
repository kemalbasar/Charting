# Import required libraries and modules
from datetime import date

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
import requests
import json
from config import reengen_company,reengen_password,reengen_username,valftoreeg
from run.agent import ag


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
dcc.DatePickerRange(
        id='date-picker',
        start_date='2023-10-03',
        end_date='2023-10-05',
        display_format='YYYY-MM-DD',
    ),
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



@app.callback(
    Output("data_table", "data"),
    Output("data_table", "columns"),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_table(s_date,f_date):
    with open(f"F:\pycarhm projects\Charting\queries\energyuse_test.sql", 'r') as file:
        filedata = file.read()
    print(s_date)
    print(f_date)
    s_date = s_date.replace('-','',2)
    f_date = f_date.replace('-','',2)
    filedata = filedata.replace("xxxx-yy-zz",s_date)
    filedata = filedata.replace("aaaa-bb-cc",f_date)
    print("************")

    print(filedata)
    df_works = ag.run_query(filedata)
    print("************")
    print(df_works)
    df_works["CONSUMPTION (kwh)"] = 0.00

    for i in range(len(df_works)):
        workcenter = df_works.iloc[i]["WORKCENTER"]
        code_wc = valftoreeg[workcenter]
        code_works = df_works.iloc[i]["WORKSTART"].strftime('%Y-%m-%dT%H:%M:%S')
        code_worke = df_works.iloc[i]["WORKEND"].strftime('%Y-%m-%dT%H:%M:%S')

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
                "resolution": "fifteenmin"
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
    df_works.sort_values(by="CONSUMPTION (kwh)", ascending=False, inplace=True)
    columns = [{"name": i, "id": i} for i in df_works.columns]
    return df_works.to_dict("records"),columns
