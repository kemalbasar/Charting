import datetime

import plotly.graph_objs as go
import dash
from dash import dcc, html, Output  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
from paho.mqtt import client as mqtt
from run.agent import ag
from valfapp.app import app
from config import project_directory

costcenters = ["PRESHANE", "CNC", "CNCTORNA", "TASLAMA"]
workcenters = ["P-12", "P-34", "P-65", "P-66", "P-16", "P-17"]
workcenters_t = "('P-12', 'P-34', 'P-65', 'P-66', 'P-16', 'P-17')"

with open(project_directory + r"\Charting\queries\mesworkcenter_data.txt", 'r') as file:
    query = file.read()

df = ag.run_query(query + ' ' +  workcenters_t)

broker_address = '172.30.134.22'
port = 1883
topic = "DevirHiz"
topic2 = "ParcaAdet"
topic3 = "SariIsik"
topic4 = "YesilIsik"
topic5 = "KırmızıIsik"


client = mqtt.Client()

try:
    client.connect(broker_address, 1883, 60)
except Exception as e:
    print(f"Failed to connect to MQTT broker. Exception: {str(e)}")


def generate_callbacks_strings():
    return [Output(f"{wc}", "figure") for wc in workcenters]


devirhizibilgisi = {}
adetbilgisi = {}
preshazir = {}
presbasıyor = {}
preskapali = {}

for wc in workcenters:
    adetbilgisi[wc] = int(0)
    devirhizibilgisi[wc] = 0
    preshazir[wc] = 0
    presbasıyor[wc] = 0
    preskapali[wc] = 0


def on_message(client, userdata, msg):
    for wc in workcenters:
        if msg.topic == wc + "/" + topic:
            devirhizibilgisi[wc] = msg.payload.decode()
        elif msg.topic == wc + "/" + topic2:
            adetbilgisi[wc] = msg.payload.decode()
        elif msg.topic == wc + "/" + topic3:
            preshazir[wc] = msg.payload.decode()
        elif msg.topic == wc + "/" + topic4:
            presbasıyor[wc] = msg.payload.decode()
        elif msg.topic == wc + "/" + topic5:
            preskapali[wc] = msg.payload.decode()


client.on_message = on_message

# Retrieve the message data from MQTT
for wc in workcenters:
    client.subscribe([(wc + "/" + topic, 0), (wc + "/" + topic2, 0),
                      (wc + "/" + topic3, 0), (wc + "/" + topic4, 0), (wc + "/" + topic5, 0)])

client.loop_start()


def generate_workcenter_layout():
    """
    this method generates the layout of the dashboard, its layout the figures as 3 workcenter for 1 row and 2 columns
    :return: list of dash rows
    """
    layout = []
    for i in range(0, len(workcenters), 3):
        layout.append(dbc.Row([
            dbc.Col(
                dcc.Graph(id=f"{workcenters[i]}"),
                width=4,
                style={'border': '1px solid white', 'padding': 0}
            ),
            dbc.Col(
                dcc.Graph(id=f"{workcenters[i + 1]}"),
                width=4,
                style={'border': '1px solid white', 'padding': 0}
            ),
            dbc.Col(
                dcc.Graph(id=f"{workcenters[i + 2]}"),
                width=4,
                style={'border': '1px solid white', 'padding': 0}
            )],

            style={'padding': 0}
        ))
    return layout


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


html.Div(children=[dcc.Graph(id=f"{wc}") for wc in workcenters],
         style={"height": 800})

layout = html.Div(children=[
    dcc.Store(id="store-bgcolor"),
    dcc.Store(id="list_of_wcs"),
    dcc.Interval(id="bgcolor-interval", interval=1000),
    dbc.Row([
        dcc.Dropdown(
            id="costcenter",
            options=[{"label": cc, "value": cc} for cc in costcenters],
            multi=False,
            value="PRESHANE",
            style={"color": "green", "background-color": "DimGray", 'width': 200}
        ),
        html.Div(children=generate_workcenter_layout(),
                 style={'width': '100%', 'height': '100%'}),
        dcc.Interval(
            id='interval-component',
            interval=5000,  # Update interval in milliseconds
            n_intervals=0
        ),
    ]),
    # set margin to zero to omit empty spaces at the right and the left
])


@app.callback(
    dash.dependencies.Output("store-bgcolor", "data"),
    [dash.dependencies.Input("bgcolor-interval", "n_intervals")]
)
def update_bgcolor(n_intervals):
    bgcolor = {wc: "red" for wc in workcenters}
    for wc in workcenters:

        print("*****")
        print(wc)
        print(preshazir[wc])
        print(presbasıyor[wc])
        print(preskapali[wc])
        print("*****")

        if presbasıyor[wc] == 'true' or presbasıyor[wc] == '1':
            bgcolor[wc] = "ForestGreen"
        elif preshazir[wc] == 'true' or preshazir[wc] == '1':
            bgcolor[wc] = "yellow"
        elif preskapali[wc] == 'true' or preskapali[wc] == '1':
            bgcolor[wc] = "red"
        else:
            bgcolor[wc] = "grey"
    return bgcolor


@app.callback(generate_callbacks_strings(),
              [dash.dependencies.Input("interval-component", "n_intervals"),
               dash.dependencies.Input("store-bgcolor", "data")
               ])
def update_graph(n, bgcolor):
    # print(bgcolor)
    # Process the message data and create the plot
    figs = []
    for workcenter in workcenters:
        # while adetbilgisi[workcenter] is None:
        #     continue
        x_data = int(df.loc[df["WORKCENTER"] == workcenter, "PARTITION"]) * int(adetbilgisi[workcenter])
        #        print(adetbilgisi)
        ndevirhizi = int(df.loc[df["WORKCENTER"] == workcenter, "NDEVIRHIZI"])
        y_data = calculate_current_optimal_qty(int(df.loc[df["WORKCENTER"] == workcenter, "OPTIMALMIKTAR"]))
        bar_color = "ForestGreen" if x_data > y_data else "red"
        # print(presbasıyor)
        # print(bgcolor)
        material = df.loc[df["WORKCENTER"] == workcenter, "MATERIAL"].tolist()[0]

        if bgcolor[workcenter] == 'grey':
             atext = "MAKİNA VERİSİ YOKTUR"
        else:
            atext = f"- Devir Hızları: {ndevirhizi}\{devirhizibilgisi[workcenter] if bgcolor[workcenter] == 'ForestGreen' else 0} -"

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=x_data,
            number={'font': {'color': 'white', 'size': 50}},
            title={"text": f"{workcenter}", "font": {"size": 40, "color": "white"}},
            delta={"reference": y_data, "valueformat": ".0f",
                   "increasing": {"color": "lime"}, "decreasing": {"color": "brown"}, "font": {"size": 40}},
            gauge={
                "axis": {"range": [None, int(df.loc[df["WORKCENTER"] == workcenter, "OPTIMALMIKTAR"])],
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



