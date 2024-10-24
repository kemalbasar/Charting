import numpy as np
import pandas as pd
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_table import DataTable
import plotly.graph_objs as go
import plotly.express as px
from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb, project_directory
import time
import random

# Create the rows for each attribute
attributes = [
    ("Operatör Adı", 'operator-name'),
    ("Malzeme", 'material'),
    ("İzleme Numarası", 'part-number'),
    ("Toplam Üretim", 'total-production'),
    ("Ret Adeti", 'ret-count'),
    ("Ölçüm Kamerası", 'measurement-camera'),
    ("Görüntü Kamerası", 'image-camera'),
    ("PPM Oranı", 'ppm-rate'),
    ("Çalışma Süresi", 'working-time'),
    ("Duruş Süresi", 'stop-time'),
    ("Sn de Denetlenen Ürün Adeti", 'checked-product-count'),
    ("OEE Değeri", 'oee-value')
]

def generate_machine_layout(machine_ids):
    # Create the table headers (fixed across all machines)
    table_headers = [
        html.Tr(children=[
            html.Td("Kolonlar / Makinalar", style={'border': '1px solid black', 'font-weight': 'bold', 'border-collapse': 'collapse'}),
        ] + [html.Td(f"Kamera - 0{machine_id}", style={'border': '1px solid black', 'font-weight': 'bold'}) for machine_id in machine_ids])
    ]

    rows = []
    for attr_name, attr_id in attributes:
        row = html.Tr(children=[
            html.Td(attr_name, style={'border': '1px solid black', 'font-weight': 'bold'})
        ] + [
            html.Td(id=f'{attr_id}-{machine_id}', style={'border': '1px solid black'}) for machine_id in machine_ids
        ])
        rows.append(row)

    # Combine headers and rows into the table
    machine_layout = html.Div(
        style={
            'border': '2px solid black', 'width': '100%', 'min-width': '500px',
            'border-collapse': 'collapse', 'margin': '0 auto', 'padding': '10px', 'margin-bottom': '20px'
        },
        children=[
            html.H3("Üretim Takip Sistemi",
                    style={'text-align': 'center', 'background-color': '#F0F0F0', 'padding': '10px',
                           'border-bottom': '2px solid black', 'color': 'black', 'font-weight': 'bold'}),
            html.Table(
                style={'width': '100%', 'border-collapse': 'collapse', 'color': 'black'},
                children=table_headers + rows  # Add headers and data rows
            )
        ]
    )

    return machine_layout


# Function to generate the shift data table
def create_shift_table(data2):
    # Pivot the data2 to get machine names as rows and shift types as columns
    pivot_data = data2.pivot(index='MACHINE', columns='SHIFTAYK', values='QUANTITY').fillna(0)

    # Prepare the table data for DataTable (converting the DataFrame to a format DataTable can understand)
    table_data = pivot_data.reset_index().to_dict('records')

    # Prepare the columns for DataTable (first column is MACHINE, others are shift types)
    table_columns = [{"name": "Makinalar", "id": "MACHINE"}] + \
                    [{"name": str(col), "id": str(col)} for col in pivot_data.columns]

    return table_data, table_columns


# Layout of the app
layout = html.Div(
    id="main-container",
    children=[
        html.Div(
            children=[generate_machine_layout(range(1, 7))],  # Now all machines are in one table
            style={'width': '100%'}  # Adjust width accordingly
        ),
        dcc.Interval(
            id='interval-component',
            interval=100000,  # in milliseconds
            n_intervals=0
        ),
        html.Div([
            html.H3("Vardiya Üretimleri",
                    style={"text-align": "center", 'color': 'black', 'padding': '10px',
                           'border-bottom': '2px solid black', 'font-weight': 'bold'}),
            DataTable(
                id='shift-table',
                columns=[],  # Initially empty, will be filled by the callback
                data=[],  # Initially empty, will be filled by the callback
                style_table={
                    'height': '300px',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '70%',
                    'width': '100%',
                    'text-align': 'center',
                    'color': 'black',
                },
                style_header={
                    'fontWeight': 'bold',
                    'color': 'black',
                    'text-align': 'center',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '16px',
                    'border': '1px dotted brown',
                    'borderRadius': '2px'
                },
            )
        ])
    ]
)

@app.callback(
    [Output(f'{attr_id}-{machine_id}', 'children') for machine_id in range(1, 7) for attr_name, attr_id in attributes],  # Updated to fill columns
    [Output(f'ppm-rate-{machine_id}', 'style') for machine_id in range(1, 7)],  # Add outputs for styling ppm-rate cells
    [Output(f'checked-product-count-{machine_id}', 'style') for machine_id in range(1, 7)],  # Add outputs for styling ppm-rate cells
    [Input("interval-component", "n_intervals")]
)
def update_machine_table(n):
    updated_data = []
    ppm_styles = []
    product_count_style = []

    for machine_id in range(1, 7):
        # Fetch and preprocess data for each machine
        query_path = project_directory + r"\Charting\queries\livekamera.sql"
        text_to_find = ["XYZ"]
        text_to_put = [f"KMR-0{machine_id}"]

        time.sleep(2)
        data = ag.editandrun_query(query_path, text_to_find, text_to_put)

        starttime = datetime.now().strftime("%Y-%m-%d")
        endtime = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        query_path2 = project_directory + r"\Charting\queries\livekamera_vardiya.sql"
        text_to_find2 = ["XYZ", "XXXX-XX-XX", "YYYY-YY-YY"]
        text_to_put2 = [f"KMR-0{machine_id}", starttime, endtime]

        data2 = ag.editandrun_query(query_path2, text_to_find2, text_to_put2)
        data["PRDORDER"] = data["PRDORDER"].apply(lambda x: x.split('\x00', 1)[0] if isinstance(x, str) and x is not None else None)

        data["MATERIAL"] = data["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0] if x else None)
        data["NAME"] = data["NAME"].astype(str)
        data["MACHINE"] = data["MACHINE"].astype(str)
        data['QUANTITY'] = data['QUANTITY'].fillna(0).astype(int)
        data['NOTOK'] = data['NOTOK'].fillna(0).astype(int)
        data['NOTOKGORSEL'] = data['NOTOKGORSEL'].fillna(0).astype(int)
        data['NOTOKOLCUSEL'] = data['NOTOKOLCUSEL'].fillna(0).astype(int)
        data['WORKINGTIME'] = data['WORKINGTIME'].fillna(0).astype(int)
        data['TOTALTIME'] = data['TOTALTIME'].fillna(0).astype(int)
        data['FAILURETIME'] = data['FAILURETIME'].fillna(0).astype(int)
        data['SANIYE_DENETLENEN'] = data['SANIYE_DENETLENEN'].fillna(0).astype(float)
        data['OEE'] = data['OEE'].fillna(0).astype(float)
        data['PPM'] = data['PPM'].fillna(0).astype(int)


        if data.empty:
            operator_name = "No Data"
            material = "No Data"
            part_number = "No Data"
            total_production = 0
            ret_count = 0
            measurement_camera = 0
            image_camera = 0
            ppm_rate = 0
            working_time = 0
            stop_time = 0
            checked_product_count = 0
            oee_value = 0
        else:
            operator_name = data["NAME"].iloc[0]
            material = data['MATERIAL'].iloc[0]
            part_number = data['PRDORDER'].iloc[0]
            total_production = data['QUANTITY'].iloc[0]
            ret_count = data['NOTOK'].iloc[0]
            measurement_camera = data['NOTOKOLCUSEL'].iloc[0]
            image_camera = data['NOTOKGORSEL'].iloc[0]
            ppm_rate = data['PPM'].iloc[0]
            working_time = data['WORKINGTIME'].iloc[0]
            stop_time = data['FAILURETIME'].iloc[0]
            checked_product_count = data['SANIYE_DENETLENEN'].iloc[0]
            oee_value = data['OEE'].iloc[0]

        # Add the data for this machine into updated_data column-wise
        machine_data = [
            operator_name, material, part_number, total_production, ret_count, measurement_camera, image_camera,
            ppm_rate, working_time, stop_time,  checked_product_count, oee_value
        ]

        updated_data.extend(machine_data)  # Ensure machine data is appended column-wise

        if ppm_rate > 2500:
            ppm_styles.append({'background-color': 'red', 'font-weight': 'bold'})
        else:
            ppm_styles.append({'background-color': 'green', 'font-weight': 'bold'})

        if checked_product_count < 6.5:
            product_count_style.append({'background-color': 'red', 'font-weight': 'bold'})
        else:
            product_count_style.append({'background-color': 'green', 'font-weight': 'bold'})

    return updated_data + ppm_styles + product_count_style  # Return all the data as a flat list


@app.callback(
    Output('shift-table', 'data'),
    Output('shift-table', 'columns'),
    [Input("interval-component", "n_intervals")]
)
def update_shift_table(n):
    starttime = datetime.now().strftime("%Y-%m-%d")
    endtime = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Initialize an empty list to hold all machine data
    all_data = []

    for machine_id in range(1, 7):
        query_path2 = project_directory + r"\Charting\queries\livekamera_vardiya.sql"
        text_to_find2 = ["XYZ", "XXXX-XX-XX", "YYYY-YY-YY"]
        text_to_put2 = [f"KMR-0{machine_id}", starttime, endtime]

        # Fetch data for the current machine
        data2 = ag.editandrun_query(query_path2, text_to_find2, text_to_put2)

        print(f"DATA for Machine {machine_id}:")
        print(data2)

        # Ensure the relevant columns are in the correct format
        data2['MACHINE'] = data2['MACHINE'].astype(str)
        data2['SHIFTAYK'] = data2['SHIFTAYK'].astype(str)
        data2['QUANTITY'] = data2['QUANTITY'].fillna(0).astype(int)
        ##data2.rename(columns={'MACHINE': 'Makinalar'}, inplace=True)

        # Append the data for this machine to the all_data list
        all_data.append(data2)

    # Concatenate all the machine data into a single DataFrame
    combined_data = pd.concat(all_data, ignore_index=True)

    # Generate the table data and columns by pivoting the combined data
    table_data, table_columns = create_shift_table(combined_data)

    return table_data, table_columns



if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)

