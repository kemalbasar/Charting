from paho.mqtt import client as mqtt_client

broker = '10.50.27.18'
port = 1883
topic = "Montaj/Fix/OkAdet"
username = 'mqtt'
password = '!Valfsan2022**!'
client_id = '159753'



def on_message(client, userdata, msg):
    print(f"Message received [{msg.topic}]: {msg.payload}")

client = mqtt_client.Client(client_id)
client.username_pw_set(username, password)
client.connect(broker, port)
client.subscribe(topic,qos=0)
client.on_message = on_message
client.loop_forever()


client.publish("house/light","on")

