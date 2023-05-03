from paho.mqtt import client as mqtt
import time

broker = '172.30.134.22'
port = 1883
topic = "P12/DevirHiz"
topic2 = "P12/ParcaAdetTest"
topic3 = "P12/SariIsik"
topic4 = "P12/YesilIsik"
username = ''
password = ''
client_id = ''
adetbilgisi = None


def on_message(client, userdata, msg):
    global adetbilgisi
    current_message = msg.payload.decode()


client = mqtt.Client()
# client.username_pw_set(username, password)
client.on_message = on_message
client.connect(broker, 1883, 60)

client.subscribe(topic4,0)

client.loop_start()

while adetbilgisi is None:
    pass

# Print the current message
print("Current message: ", adetbilgisi)

client.loop_stop()

client.publish("P12/AdetRst",True)

