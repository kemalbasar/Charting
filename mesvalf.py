import datetime
import warnings
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px  # (version 4.7.0 or higher)
import dash
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
from paho.mqtt import client as mqtt
from run.agent import ag

df = ag.run_query(r"C:\Users\kereviz\PythonP\Charting\queries")

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.SLATE],
)
server = app.server

broker_address = '172.30.134.22'
port = 1883
topic = "P12/DevirHiz"
topic2 = "P12/ParcaAdet"
topic3 = "P12/SariIsik"
topic4 = "P12/YesilIsik"

client = mqtt.Client()

client.connect(broker_address, 1883, 60)

client.publish("P12/AdetRstTest", "reset", 2)


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


client.on_message = on_message

adetbilgisi = None
devirhizibilgisi = 80
preshazir = False
print(preshazir)
print("bura")
presbasıyor = False


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


costcenters = ["CNC", "CNCTORNA", "TASLAMA"]

app.layout = html.Div(children=
[dbc.Container([

    dbc.Row([dcc.Dropdown(id="costcenter",
                          options=[{"label": cc, "value": cc} for cc in costcenters],
                          multi=False,
                          value="CNC",
                          style={"color": "green", "background-color": "DimGray", 'width': 200}
                          )
                ,
             html.Div(dcc.Graph(id="live-graph", style={"margin-top": 20, "height": 600}))])]),
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update interval in milliseconds
        n_intervals=0
    )
]
)


@app.callback(dash.dependencies.Output("live-graph", "figure"),
              [dash.dependencies.Input("interval-component", "n_intervals")])
def update_graph(n):
    # Retrieve the message data from MQTT
    client.subscribe([(topic, 0), (topic2, 0), (topic3, 0), (topic4, 0)])
    client.loop_start()

    # Process the message data and create the plot
    while adetbilgisi is None:
        continue
    x_data = int(df.loc[df["WORKCENTER"] == 'P-12', "PARTITION"]) * int(adetbilgisi) + 20000
    ndevirhizi = int(df.loc[df["WORKCENTER"] == 'P-12', "NDEVIRHIZI"])
    print(ndevirhizi)
    print(devirhizibilgisi)
    # print("current")
    # print(adetbilgisi)/6
    # print("optm")
    # print(calculate_current_optimal_qty(int(df.loc[df["WORKCENTER"] == 'P-30',"OPTIMALMIKTAR"])))
    y_data = calculate_current_optimal_qty(int(df.loc[df["WORKCENTER"] == 'P-12', "OPTIMALMIKTAR"]))
    bar_color = "ForestGreen" if x_data > y_data else "red"
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

    bgcolor = "yellow" if preshazir else ("ForestGreen" if presbasıyor else "red")
    # material = df.loc[df["WORKCENTER"] == 'P-12', "MATERIAL"].tolist()[0]
    # performance = f"Tahmin\n %{}"
    fig.update_layout(
        annotations=[
            go.layout.Annotation(
                x=1.01,
                y=-0.2,
                xref='paper',  # we'll reference the paper which we draw plot
                yref='paper',
                showarrow=False,
                text=f"İdeal Devir Hızı : {ndevirhizi} --- Anlık Devir Hızı: {devirhizibilgisi}",
                font=dict(
                    size=50,
                    color="black"
                )
            )
        ],
        paper_bgcolor=bgcolor
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
