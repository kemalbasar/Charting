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



#get point hierarchy

# ********************************************# ********************************************# ********************************************
# ********************************************# ********************************************# ********************************************

# Headers
headers = {
    'Content-Type': 'application/json',
    'XConnectionId': connection_id,       # Replace with your connection id
    'XLang': 'valfsan'               # Replace with your tenant name
}

# # Payload for GetPointHierarchy
# payload = {
#     "$": "GetPointHierarchy"
# }
#
# # Make the POST request
# response = requests.post(url, data=json.dumps(payload), headers=headers)
#
# # Check if the request was successful
# if response.status_code == 200:
#     response_data = response.json()
#     print(json.dumps(response_data, indent=4))   # Pretty print the JSON response
# else:
#     print(f"HTTP Error: {response.status_code}")
# get_hierarchy = { "$": "GetPointHierarchy"}
#
# response = requests.post(url, data=json.dumps(auth_payload), headers=headers)
#

# ********************************************# ********************************************# ********************************************
# ********************************************# ********************************************# ********************************************

# s_date = '20231002'
# f_date = '20231005'
# with open(f"F:\pycarhm projects\Charting\queries\mest_test.sql", 'r') as file:
#     filedata = file.read()
# s_date = s_date.replace('-', '', 2)
# f_date = f_date.replace('-', '', 2)
# filedata = filedata.replace("xxxx-yy-zz", s_date)
# filedata = filedata.replace("aaaa-bb-cc", f_date)
# print(filedata)
# df_works = ag.run_query(filedata)
# df_works["CONSUMPTION"] = 0.00

# for i in range(len(df_works)):
#     workcenter = df_works.iloc[i]["WORKCENTER"]
#     code_wc = valftoreeg[workcenter]


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
        "point": ["valfsan_taslama_dd_02"],
        "start": "2023-11-01T00:00:00",
        "end": "2023-11-30T00:00:00",
        "break": {
            "type": "point"
        },
        "resolution": "day"
    }
}

# Make the POST request
response = requests.post(url, data=json.dumps(payload), headers=headers)

# Check if the request was successful
if response.status_code == 200:
    response_data = response.json()
    print(json.dumps(response_data, indent=4))  # Pretty print the JSON response
else:
    print(f"HTTP Error: {response.status_code}")