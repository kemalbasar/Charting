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




# headers = {
#     'Content-Type': 'application/json',
#     'XConnectionId': connection_id,       # Replace with your connection id
#     'XLang': 'valfsan'               # Replace with your tenant name
# }
#
# # Payload for GetPointHierarchy
# payload = {
#     "$": "GetPointHierarchy"
# }
#
# # Make the POST request
# response = requests.post(url, data=json.dumps(payload), headers=headers)
# 0
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


1

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
        "point": ["valfsan_salter5"],
        "start": "2023-10-04T07:20:39.000",
        "end": "2023-10-04T23:40:58.000",
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
    print(json.dumps(response_data, indent=4))  # Pretty print the JSON response
else:
    print(f"HTTP Error: {response.status_code}")