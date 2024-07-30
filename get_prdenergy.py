
from config import reengen_company, reengen_password, reengen_username
from config import server, username, password, database
import pyodbc
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from config import project_directory, valftoreeg
import requests
import json

from run.agent import ag

# API Endpoint
url = "https://api.reengen.com/api/do/"
#
#
# Authentication payload
auth_payload = {
    "$": "Authenticate",
    "properties": {
        "tenant": reengen_company,  # Replace with your tenant name
        "user": reengen_username,  # Replace with your username
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

# Headers

connection = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')


begin_month = 3
begin_year = 2024
final_month = 5
final_year = 2024


start_date = datetime(begin_year, begin_month,12)
end_date = datetime(final_year, final_month, 30)
difference = relativedelta(end_date, start_date)

end_date = end_date.strftime('%Y-%m-%d %H:%M:%S.%f')
start_date = start_date.strftime('%Y-%m-%d %H:%M:%S.%f')






df = ag.run_query(query=r"EXEC [VLFENERGYPRD] @WORKSTART=?, @WORKEND=?", params=[start_date,end_date])
df.reset_index(inplace=True)

for index, row in df.iterrows():

    row.WORKSTART = row.WORKSTART.strftime('%Y-%m-%dT%H:%M:%S')
    row.WORKEND = row.WORKEND.strftime('%Y-%m-%dT%H:%M:%S')
    query = f"SELECT MPOINT,RATE FROM VLFENRGY001 WHERE STEXT = '{row['WORKCENTER']}' AND ISFIRST = 1"
    df_mpoint = ag.run_query(query)

    try:
        tmp_mpoint =  df_mpoint["MPOINT"][0]
    except:
        print(f"{row['WORKCENTER']} iş merkezi için KWH verisi bulunamadı")
        continue

    if df_mpoint["MPOINT"][0] == 'valfsan_pano1_preshane1,valfsan_salter5,valfsan_salter2,valfsan_salter3' or \
            df_mpoint["MPOINT"][0] == "valfsan_pano2_preshane1,valfsan_preshaneemisfani_11kw":
        mpoint_list = df_mpoint["MPOINT"][0].split(',')
        totval = 0.00
        for item in mpoint_list:
            tmp_mpoint = item
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
                    "point": [tmp_mpoint],
                    "start": row["WORKSTART"],
                    "end": row["WORKEND"],
                    "break": {
                        "type": "point"
                    },
                    "resolution": "fifteenmin"
                }
            }
            # print(payload)
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

            if response_data["properties"]["data"]['0'] is not None:
                total_kwh = 0.000
                for item in response_data["properties"]["data"]['0']:
                    total_kwh = total_kwh + round(float(item[2]), 4)

                if mpoint_list[0] == item:
                    totval = totval + total_kwh
                else:
                    totval = totval - total_kwh

        totval = totval*float(df_mpoint["RATE"])

        with open('example.txt', 'a') as file:

            sql = f"INSERT INTO VLFPRDENERGY (MATERIAL, OUTPUT, COSTCENTER, WORKCENTER, QTY, KWH, WORKSTART, WORKEND, CONFIRMATION, CONFIRMPOS, WORKINGHOUR, MPOINT, SETUPTIME, IDEALCYCLETIME) " \
                  f"VALUES ('{row['MATERIAL']}', 0, '{row['COSTCENTER']}', '{row['WORKCENTER']}', {row['QTY']},{totval}, '{row['WORKSTART']}', '{row['WORKEND']}', {row['CONFIRMATION']}, {row['CONFIRMPOS']}, {row['WORKINGHOUR']}, '{tmp_mpoint}', {row['SETUPTIME']}, {row['IDEALCYCLETIME']})"

            print(sql)
            file.write(sql)
            file.write("\n")


    else:
        tmp_mpoint =  df_mpoint["MPOINT"][0]
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
                "point": [tmp_mpoint],
                "start": row["WORKSTART"],
                "end": row["WORKEND"],
                "break": {
                    "type": "point"
                },
                "resolution": "fifteenmin"
            }
        }
        # print(payload)
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



        with open('example.txt', 'a', encoding='utf-8') as file:
            if response_data["properties"]["data"]['0'] is not None:
                total_kwh = 0.000
                for item in response_data["properties"]["data"]['0']:

                    total_kwh = total_kwh + round(float(item[2]), 4)

                sql = f"INSERT INTO VLFPRDENERGY (MATERIAL, OUTPUT, COSTCENTER, WORKCENTER, QTY, KWH, WORKSTART, WORKEND, CONFIRMATION, CONFIRMPOS, WORKINGHOUR, MPOINT, SETUPTIME, IDEALCYCLETIME) " \
                      f"VALUES ('{row['MATERIAL']}', 0, '{row['COSTCENTER']}', '{row['WORKCENTER']}', {row['QTY']},{total_kwh}, '{row['WORKSTART']}', '{row['WORKEND']}', {row['CONFIRMATION']}, {row['CONFIRMPOS']}, {row['WORKINGHOUR']}, '{tmp_mpoint}', {row['SETUPTIME']}, {row['IDEALCYCLETIME']})"

                print(sql)
                file.write(sql)
                file.write("\n")
            else:
                sql = f"INSERT INTO VLFPRDENERGY (MATERIAL, OUTPUT, COSTCENTER, WORKCENTER, QTY, KWH, WORKSTART, WORKEND, CONFIRMATION, CONFIRMPOS, WORKINGHOUR, MPOINT, SETUPTIME, IDEALCYCLETIME) " \
                      f"VALUES ('{row['MATERIAL']}', 0, '{row['COSTCENTER']}', '{row['WORKCENTER']}', {row['QTY']},{0}, '{row['WORKSTART']}', '{row['WORKEND']}', {row['CONFIRMATION']}, {row['CONFIRMPOS']}, {row['WORKINGHOUR']}, '{tmp_mpoint}', {row['SETUPTIME']}, {row['IDEALCYCLETIME']})"

                print(sql)
                file.write(sql)
                file.write("\n")

                # sql = '''INSERT INTO VLFENERGY (DATE,MPOINT,SCODE,OUTPUT,COSTCENTER,INTERVAL)
                #          VALUES (?, ?, ?, ?, ?, ?)'''
                # print(sql)
                # agiot.run_query(sql,params,0)


