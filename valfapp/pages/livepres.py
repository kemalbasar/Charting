import datetime

import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc, html, Input, Output, State, exceptions
import dash_bootstrap_components as dbc
from paho.mqtt import client as mqtt
from run.agent import ag
from valfapp.app import app
from config import project_directory

costcenters = ["PRESHANE", "TAMBUR"]

with open(project_directory + r"\Charting\queries\mesworkcenter_data.txt", 'r') as file:
    query = file.read()

failure_codes = {
    "D104_0 ": "Cont.",
    'D104_1': 'Single',
    'D104_2': 'Inch.',
    'D104_3': 'Manual',
    'D124_0': 'No Err.',
    'D124_1': 'Motor Unstart',
    'D124_2': 'EMG Stop',
    'D124_3': 'Lub. Fault',
    'D124_4': 'MisfeeD 1 Fault',
    'D124_5': 'Mat. 1 Fault',
    'D124_7': 'Air Pressure Fault',
    'D124_9': 'Inverter Fault',
    'D124_10': 'Cumulate Arrival',
    'D124_11': 'Cumulate Arrival',
    'D124_12': 'Manual',
    'D124_12': 'Reverse',
    'D124_14': 'EncoDer Disconnect',
    'D124_20': 'MisfeeD 2 Fault',
    'D124_21': 'Start Fault',
    'D124_27': 'Lock Fault',
    'D124_28': 'Lock Not Relief',
    'D124_42': 'B.D.C Det.',
    'D124_43': 'Tonnage Fault',
    'D124_44': 'MisfeeD 3 Fault',
    'D124_45': 'MisfeeD 4 Fault',
    'D124_47': 'Communication Timeout',
}

broker_address = '172.30.134.22'
port = 1883

topcis_in = {"out/OpMode": "out/OpMode", "out/OpStatus": "out/OpStatus", "out/OpSpeed": "out/OpSpeed",
             "out/CamAngle": "out/CamAngle", "out/GreenLight": "out/GreenLight", "out/CurrentPiece": "out/CurrentPiece"}
topics_out = {"dur": "in/TDCStop", "hazır": "in/Start"}

topic = topcis_in["out/OpSpeed"]
topic2 = topcis_in["out/CurrentPiece"]
topic3 = topcis_in["out/OpStatus"]
topic4 = topcis_in["out/CamAngle"]
topic5 = topcis_in["out/OpMode"]
topic6 = topcis_in["out/GreenLight"]


wclist = ["P-14", "P-26", "P-67", "P-68"]

a = ()
for w in wclist:
    a = a + (w,)
a = "('" + "','".join(map(str, a)) + "')"
print(f"{query} {a}")

global dfff
dfff = ag.run_query(query + ' ' + a)
# dfff = dfff.to_json(date_format='iso', orient='split')
dfff.loc[len(dfff.index)] = [0, 'P-77', 'TEST', 2, 300, 10000, 100000]
dfff.loc[len(dfff.index)] = [0, 'P-75', 'TEST', 2, 300, 10000, 100000]

client = mqtt.Client()

try:
    client.connect(broker_address, 1883, 60)
except Exception as e:
    print(f"Failed to connect to MQTT broker. Exception: {str(e)}")

callbacks_strings = [Output(f"{wc}", "figure") for wc in wclist]


def calculate_current_optimal_qty(optimalqty):
    # Define the current time
    now = datetime.datetime.now()
    # Define the target time
    if (datetime.datetime.now().strftime("%H:%M:%S") > '23:00:00') & \
            ((datetime.datetime.now().strftime("%H:%M:%S") > '00:00:00') &
             (datetime.datetime.now().strftime("%H:%M:%S") < '07:00:00')):
        target_time = datetime.time(hour=23, minute=00)
    elif ((datetime.datetime.now().strftime("%H:%M:%S") > '07:00:00') &
          (datetime.datetime.now().strftime("%H:%M:%S") < '15:00:00')):
        target_time = datetime.time(hour=7, minute=00)
    else:
        target_time = datetime.time(hour=15, minute=00)

    # Combine the current date and target time
    target_datetime = datetime.datetime.combine(now.date(), target_time)
    # Calculate the minute difference between the current time and target time
    minute_diff = int((now - target_datetime).total_seconds() / 60)
    return optimalqty * (minute_diff / 420)


# html.Div(children=[dcc.Graph(id=f"{wc}") for wc in workcenters],
#          style={"height": 800})

layout = html.Div(children=[
    dcc.Store(id='nothing'),
    dcc.Store(id="store-bgcolor"),
    dcc.Store(id="df_infos_t"),
    dcc.Store(id="workcenter_list", storage_type='memory', data=wclist),
    dcc.Store(id="workcenter_list_b", storage_type='memory', data=wclist),
    dcc.Store(id="workcenter_list_c", storage_type='memory', data=wclist),
    dcc.Interval(id="bgcolor-interval", interval=5000),
    dbc.Row(dcc.Link(
        children='Main Page',
        href='/',
        style={"height": 40, "color": "black", "font-weight": "bold"}

    )),
    dbc.Row([
        dbc.Button(id='emg_stop', className='estop-button'),
        dcc.Dropdown(
            id="costcenter",
            options=[{"label": cc, "value": cc} for cc in costcenters],
            value="PRESHANE",
            style={"color": "green", "background-color": "DimGray", 'width': 200}
        ),
        dcc.Interval(
            id='interval-component',
            interval=5000,  # Update interval in milliseconds
            n_intervals=0
        ),
        html.Div(id='main-layout-div-live')
    ]),
    # set margin to zero to omit empty spaces at the right and the left
])


@app.callback(
    Output(component_id='workcenter_list', component_property='data'),
    Input(component_id='costcenter', component_property='value'),
)
def update_lists(costcenter):
    global callbacks_strings
    callbacks_strings = [Output(f"{wc}", "figure") for wc in wclist]
    if costcenter == 'PRESHANE':
        list = wclist
        list_t = str(tuple(listreport))
    else:
        list = ["T-33", "T-34", "T-35", "T-36", "T-37", "T-38"]
        list_t = "('T-33', 'T-34', 'T-35', 'T-36', 'T-37', 'T-38')"

    global opspeed
    opspeed = {}
    global currentpiece
    currentpiece = {}
    global opstatus
    opstatus = {}
    global camangle
    camangle = {}
    global opmode
    opmode = {}
    global greenlight
    greenlight = {}

    for wc in list:
        currentpiece[wc] = int(0)
        opspeed[wc] = 0
        opstatus[wc] = 999
        camangle[wc] = 0
        opmode[wc] = 0
        greenlight[wc] = 0

    def on_message(client, userdata, msg):
        for wc in list:
            if msg.topic == wc + "/" + topic:
                opspeed[wc] = msg.payload.decode()
            elif msg.topic == wc + "/" + topic2:
                currentpiece[wc] = msg.payload.decode()
            elif msg.topic == wc + "/" + topic3:
                opstatus[wc] = msg.payload.decode()
            elif msg.topic == wc + "/" + topic4:
                camangle[wc] = msg.payload.decode()
            elif msg.topic == wc + "/" + topic5:
                opmode[wc] = msg.payload.decode()
            elif msg.topic == wc + "/" + topic6:
                greenlight[wc] = msg.payload.decode()

    def on_publish(client, userdata, mid):
        print("Message Published...")

    client.on_publish = on_publish
    client.on_message = on_message

    # Retrieve the message data from MQTT
    for wc in list:
        client.subscribe([(wc + "/" + topic, 0), (wc + "/" + topic2, 0),
                          (wc + "/" + topic3, 0), (wc + "/" + topic4, 0), (wc + "/" + topic5, 0),
                          (wc + "/" + topic6, 0)])

    client.loop_start()
    return list


@app.callback(
    [Output('main-layout-div-live', 'children'),
     Output('workcenter_list_b', 'data')],
    Input('workcenter_list', 'data'))
def generate_workcenter_layout(workcenters):
    """
    this method generates the layout of the dashboard, its layout the figures as 3 workcenter for 1 row and 2 columns
    :return: list of dash rows
    """

    layout = []
    workcenters.append
    for i in range(0, len(workcenters), 3):
        layout.append(dbc.Row([
            dbc.Col(
                dcc.Graph(id=f"{workcenters[i]}"),
                width=4,
                style={'border': '1px solid white', 'padding': 0}
            ),
            dbc.Col(
                [] if i+2 > len(workcenters)  else dcc.Graph(id=f"{workcenters[i + 1]}"),
                width=4,
                style={'border': '1px solid white', 'padding': 0}
            ),
            dbc.Col(
                [] if i+2 > len(workcenters) else dcc.Graph(id=f"{workcenters[i + 2]}"),
                width=4,
                style={'border': '1px solid white', 'padding': 0}
            )],
            style={'padding': 0}
        ))
    return [layout, workcenters]


@app.callback(callbacks_strings,
              [Input(component_id='bgcolor-interval', component_property='n_intervals'),
               Input("workcenter_list_c", "data")
               ])
def update_graph(n, workcenter_list):
    workcenters = workcenter_list
    bgcolor = {wc: "red" for wc in workcenters}
    print(currentpiece)
    for wc in workcenters:

        if greenlight[wc] == '1':
            bgcolor[wc] = "ForestGreen"
        elif opstatus[wc] == 0:
            bgcolor[wc] = "orange"
        elif opstatus[wc] != 12 or opstatus[wc] != 0:
            bgcolor[wc] = "red"
        else:
            bgcolor[wc] = "grey"

    # Process the message data and create the plot
    figs = []
    global dfff
    # dfff = pd.read_json(dfff, orient='666')
    for workcenter in workcenters:
        x_data = int(dfff.loc[dfff["WORKCENTER"] == workcenter, "PARTITION"]) * int(currentpiece[workcenter])
        ndevirhizi = int(dfff.loc[dfff["WORKCENTER"] == workcenter, "NDEVIRHIZI"])
        y_data = calculate_current_optimal_qty(int(dfff.loc[dfff["WORKCENTER"] == workcenter, "OPTIMALMIKTAR"]))
        bar_color = "ForestGreen" if x_data > y_data else "red"
        material = dfff.loc[dfff["WORKCENTER"] == workcenter, "MATERIAL"].tolist()[0]

        if bgcolor[workcenter] == 'grey':
            atext = "MAKİNA VERİSİ YOKTUR"
        else:
            atext = f"- Devir Hızları: {ndevirhizi}\{opspeed[workcenter] if bgcolor[workcenter] == 'ForestGreen' else 0} -"

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=x_data,
            number={'font': {'color': 'white', 'size': 50}},
            title={"text": f"{workcenter}", "font": {"size": 40, "color": "white"}},
            delta={"reference": y_data, "valueformat": ".0f",
                   "increasing": {"color": "lime"}, "decreasing": {"color": "brown"}, "font": {"size": 40}},
            gauge={
                "axis": {"range": [None, int(dfff.loc[dfff["WORKCENTER"] == workcenter, "OPTIMALMIKTAR"])],
                         "tickcolor": "white",
                         "tickfont": {"color": "white", "size": 10}
                         },
                "steps": [
                    {"range": [0, 5], "color": "lightgray"},
                    {"range": [5, 10], "color": "gray"}
                ],
                "threshold": {
                    "line": {"color": "#ffd700", "width": 30},
                    "thickness": 1,
                    "value": y_data
                },
                "bgcolor": "MintCream",
                "bordercolor": "white",

                'bar': {'color': bar_color}
            }
        ))

        fig.update_layout(
            height=475,
            width=600,
            annotations=[

                go.layout.Annotation(
                    # x=0.76,
                    y=-0.2,
                    # xref='paper',  # we'll reference the paper which we draw plot
                    # yref='paper',
                    xanchor='center',
                    showarrow=False,
                    text=atext,
                    # if bgcolor == 'ForestGreen' else 0
                    font=dict(
                        size=30,
                        color="white"
                    )
                ),
                go.layout.Annotation(
                    x=1.15,
                    y=1.30,
                    xref='paper',  # we'll reference the paper which we draw plot
                    yref='paper',
                    showarrow=False,
                    text=f'\n{material}',
                    font=dict(
                        size=30,
                        color="white"
                    )
                )
            ],
            paper_bgcolor=bgcolor[workcenter]
        )
        figs.append(fig)

    return figs


@app.callback(Output('nothing', 'value'),
              Input('emg_stop', 'n_clicks'))
def emergency_stop(n):
    client.publish("P-76/in/EMGStop", 0, qos=0)
