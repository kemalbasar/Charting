import numpy as np
import pandas as pd
from dash import dcc, html, Input, Output, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb
from dash_table import DataTable
import time
import random
from config import kb, project_directory

from valfapp.layouts import nav_bar
import dash_html_components as html
import dash_core_components as dcc



def generate_machine_layout(machine_id):
    machine_layout = [
        html.Div(
            id=f"machine-{machine_id}",
            style={'border': '2px solid black', 'width': '100%', 'min-width': '500px', 'border-collapse': 'collapse',  'margin': '0 auto', 'padding': '10px', 'margin-bottom': '20px'},
            children=[
                html.H3(f"Kamera - 0{machine_id} Üretim Takip Sistemi", style={'text-align': 'center', 'background-color': '#F0F0F0', 'padding': '10px', 'border-bottom': '2px solid black', 'color': 'black', 'font-weight': 'bold'}),
                html.Table(
                    style={'width': '100%', 'border-collapse': 'collapse', 'color': 'black'},
                    children=[
                        html.Tr(id=f'operator-row-{machine_id}', children=[
                            html.Td("Operatör Adı", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'operator-name-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'part-number-row-{machine_id}', children=[
                            html.Td("Parça Numarası / İzleme Numarası", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'part-number-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'total-production-row-{machine_id}', children=[
                            html.Td("Toplam Üretim", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'total-production-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'ret-count-row-{machine_id}', children=[
                            html.Td("Ret Adeti", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'ret-count-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'measurement-camera-row-{machine_id}', children=[
                            html.Td("Ölçüm Kamerası", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold', 'padding-left': '20px'}),
                            html.Td(id=f'measurement-camera-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'image-camera-row-{machine_id}', children=[
                            html.Td("Görüntü Kamerası", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold', 'padding-left': '20px'}),
                            html.Td(id=f'image-camera-{machine_id}', style={'border': '1px solid black', 'color': 'black',})
                        ]),
                        html.Tr(id=f'ppm-rate-row-{machine_id}', children=[
                            html.Td("PPM Oranı", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'ppm-rate-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'working-time-row-{machine_id}', children=[
                            html.Td("Çalışma Süresi",
                                    style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'working-time-{machine_id}',
                                    style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'stop-time-row-{machine_id}', children=[
                            html.Td("Duruş Süresi",
                                    style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'stop-time-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'checked-product-count-row-{machine_id}', children=[
                            html.Td("Sn de Denetlenen Ürün Adeti",
                                    style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'checked-product-count-{machine_id}',
                                    style={'border': '1px solid black', 'color': 'black'})
                        ]),
                        html.Tr(id=f'oee-value-row-{machine_id}', children=[
                            html.Td("OEE Değeri",
                                    style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                            html.Td(id=f'oee-value-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                        ]),
                    ]
                ),
                html.Div(
                    "Bu kısma önceki kontrol edilen parçanın bilgileri koyulabilir.",
                    style={'background-color': '#3C78D8', 'color': 'black', 'padding': '20px', 'margin-top': '10px', 'text-align': 'center', 'border': '1px solid black'}
                ),
            ]
        )
    ]
    return machine_layout

layout = html.Div(
    id="main-container",
    children=[
        html.Div(
            [
                html.Div(generate_machine_layout(x), style={'display': 'inline-block', 'width': '33%'}) for x in range(1, 7)  # Displaying only 6 machines
            ],
            style={'display': 'flex', 'flex-wrap': 'wrap'}  # To wrap the machines into two rows
        ),
        dcc.Interval(
            id='interval-component',
            interval=100000  # in milliseconds
        )
    ]
)

@app.callback(
    [Output(f"machine-{machine_id}", "children") for machine_id in range(1, 7)],
    [Input("interval-component", "n_intervals")]
)
def update_machine_table(n):
    updated_layout = []
    for machine_id in range(1, 7):
        query_path = project_directory + r"\Charting\queries\livekamera.sql"
        text_to_find = ["XYZ"]
        text_to_put = [f"KMR-0{machine_id}"]

        time.sleep(2)
        data = ag.editandrun_query(query_path, text_to_find, text_to_put)

        data["PRDORDER"] = data["PRDORDER"].apply(lambda x: x.split('\x00', 1)[0] if x else None)
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
            part_number = f"{data['MATERIAL'].iloc[0]} / {data['PRDORDER'].iloc[0]}"
            total_production = data['QUANTITY'].iloc[0]
            ret_count = data['NOTOK'].iloc[0]
            measurement_camera = data['NOTOKOLCUSEL'].iloc[0]
            image_camera = data['NOTOKGORSEL'].iloc[0]
            ppm_rate = data['PPM'].iloc[0]
            working_time = data['WORKINGTIME'].iloc[0]
            stop_time = data['FAILURETIME'].iloc[0]
            checked_product_count = data['SANIYE_DENETLENEN'].iloc[0]
            oee_value = data['OEE'].iloc[0]

        ppm_rate_style = {'background-color': 'red', 'font-weight': 'bold'} if ppm_rate > 2500 else {}
        checked_product_count_style = {'background-color': 'red', 'font-weight': 'bold'} if checked_product_count < 6.5 else {}

        updated_machine_layout = [
            html.H3(f"Kamera - 0{machine_id} Üretim Takip Sistemi", style={'text-align': 'center', 'background-color': '#F0F0F0', 'padding': '10px', 'border-bottom': '2px solid black', 'color': 'black', 'font-weight': 'bold'}),
            html.Table(
                style={'width': '100%', 'border-collapse': 'collapse', 'color': 'black'},
                children=[
                    html.Tr(id=f'operator-row-{machine_id}', children=[
                        html.Td("Operatör Adı", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(operator_name, id=f'operator-name-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'part-number-row-{machine_id}', children=[
                        html.Td("Parça Numarası / İzleme Numarası", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(part_number, id=f'part-number-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'total-production-row-{machine_id}', children=[
                        html.Td("Toplam Üretim", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(total_production, id=f'total-production-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'ret-count-row-{machine_id}', children=[
                        html.Td("Ret Adeti", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(ret_count, id=f'ret-count-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'measurement-camera-row-{machine_id}', children=[
                        html.Td("Ölçüm Kamerası", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold', 'padding-left': '20px'}),
                        html.Td(measurement_camera, id=f'measurement-camera-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'image-camera-row-{machine_id}', children=[
                        html.Td("Görüntü Kamerası", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold', 'padding-left': '20px'}),
                        html.Td(image_camera, id=f'image-camera-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'ppm-rate-row-{machine_id}', children=[
                        html.Td("PPM Oranı", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(ppm_rate, id=f'ppm-rate-{machine_id}', style={**ppm_rate_style, 'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'working-time-row-{machine_id}', children=[
                        html.Td("Çalışma Süresi", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(working_time, id=f'working-time-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'stop-time-row-{machine_id}', children=[
                        html.Td("Duruş Süresi", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(stop_time, id=f'stop-time-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'checked-product-count-row-{machine_id}', children=[
                        html.Td("Sn de Denetlenen Ürün Adeti", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(checked_product_count, id=f'checked-product-count-{machine_id}', style={**checked_product_count_style, 'border': '1px solid black', 'color': 'black'})
                    ]),
                    html.Tr(id=f'oee-value-row-{machine_id}', children=[
                        html.Td("OEE Değeri", style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                        html.Td(oee_value, id=f'oee-value-{machine_id}', style={'border': '1px solid black', 'color': 'black'})
                    ]),
                ]
            ),
            html.Div(
                "Bu kısma önceki kontrol edilen parçanın bilgileri koyulabilir.",
                style={'background-color': '#3C78D8', 'color': 'black', 'padding': '20px', 'margin-top': '10px', 'text-align': 'center', 'border': '1px solid black'}
            ),
        ]
        updated_layout.append(updated_machine_layout)
    return updated_layout

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)


