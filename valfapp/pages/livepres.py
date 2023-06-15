import datetime

import plotly.graph_objs as go
import dash
from dash import dcc, html # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
from paho.mqtt import client as mqtt
from run.agent import ag
from valfapp.app import app
from config import project_directory

df = ag.run_query(project_directory + r"\Charting\queries\mesworkcenter_data.txt")



broker_address = '172.30.134.22'
port = 1883
topic = "P12/DevirHiz"
topic2 = "P12/ParcaAdet"
topic3 = "P12/SariIsik"
topic4 = "P12/YesilIsik"

client = mqtt.Client()

client.connect(broker_address, 1883, 60)

# client.publish("P12/AdetRst", True, 2)


def on_message(client, userdata, msg):
    topic_cur = msg.topic
    global adetbilgisi
    global devirhizibilgisi
    global preshazir
    global presbasıyor

    if topic_cur == topic:
        devirhizibilgisi = msg.payload.decode()
    elif topic_cur == topic2:
        adetbilgisi = msg.payload.decode()
    elif topic_cur == topic3:
        preshazir = msg.payload.decode()
    elif topic_cur == topic4:
        presbasıyor = msg.payload.decode()

# Retrieve the message data from MQTT

client.on_message = on_message
client.subscribe([(topic, 0), (topic2, 0), (topic3, 0), (topic4, 0)])
client.loop_start()

adetbilgisi = int(0)
devirhizibilgisi = 0
preshazir = False
presbasıyor = True


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


costcenters = ["PRESHANE","CNC", "CNCTORNA", "TASLAMA"]



layout = html.Div(children=
[dcc.Store(id="store-bgcolor"),dcc.Interval(id="bgcolor-interval", interval=1000),

dbc.Container([

    dbc.Row([dcc.Dropdown(id="costcenter",
                          options=[{"label": cc, "value": cc} for cc in costcenters],
                          multi=False,
                          value="PRESHANE",
                          style={"color": "green", "background-color": "DimGray", 'width': 200}
                          )
                ,
             html.Div(children=[dcc.Graph(id="live-graph", style={"margin-top": 20, "height": 800})],
                      style = {"height":800})])]),
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update interval in milliseconds
        n_intervals=0
    )
]
)

@app.callback(
    dash.dependencies.Output("store-bgcolor", "data"),
    [dash.dependencies.Input("bgcolor-interval", "n_intervals")]
)
def update_bgcolor(n_intervals):
    if presbasıyor == 'true':
        return "ForestGreen"
    elif preshazir == 'true':
        return "yellow"
    else:
        return "red"


@app.callback(dash.dependencies.Output("live-graph", "figure"),
              [dash.dependencies.Input("interval-component", "n_intervals"),
              dash.dependencies.Input("store-bgcolor", "data")

])
def update_graph(n,bgcolor):
    # Process the message data and create the plot
    while adetbilgisi is None:
        continue
    x_data = int(df.loc[df["WORKCENTER"] == 'P-12', "PARTITION"]) * int(adetbilgisi)
    ndevirhizi =int(df.loc[df["WORKCENTER"] == 'P-12', "NDEVIRHIZI"])
    y_data = calculate_current_optimal_qty(int(df.loc[df["WORKCENTER"] == 'P-12', "OPTIMALMIKTAR"]))
    bar_color = "ForestGreen" if x_data > y_data else "red"
    # print(presbasıyor)
    # print(bgcolor)
    material = df.loc[df["WORKCENTER"] == 'P-12', "MATERIAL"].tolist()[0]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=x_data,
        title={"text": "P-12", "font": {"size": 50}},
        delta={"reference": y_data,
               "increasing": {"color": "green"}, "decreasing": {"color": "red"}, "font": {"size": 80}},
        gauge={
            "axis": {"range": [None, int(df.loc[df["WORKCENTER"] == 'P-12', "OPTIMALMIKTAR"])]},
            "steps": [
                {"range": [0, 5], "color": "lightgray"},
                {"range": [5, 10], "color": "gray"}
            ],
            "threshold": {
                "line": {"color": "black", "width": 30},
                "thickness": 1,
                "value": y_data
            },
            "bgcolor": "MintCream",

            'bar': {'color': bar_color}
        }
    ))

    fig.update_layout(
        height = 800,
        annotations=[

            go.layout.Annotation(
                x=1.01,
                y=-0.1,
                xref='paper',  # we'll reference the paper which we draw plot
                yref='paper',
                showarrow=False,
                text=f"İdeal Devir Hızı : {ndevirhizi} --"
                     f"- Anlık Devir Hızı: {devirhizibilgisi if bgcolor == 'ForestGreen' else 0}",
                font=dict(
                    size=50,
                    color="black"
                )
            ),
                go.layout.Annotation(
                x=1.01,
                y=1.1,
                xref='paper',  # we'll reference the paper which we draw plot
                yref='paper',
                showarrow=False,
                text=f'\n{material}',
                font=dict(
                    size=50,
                    color="black"
                )
            )
        ],
        paper_bgcolor=bgcolor
    )
    return fig