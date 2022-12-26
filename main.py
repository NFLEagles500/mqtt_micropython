#import upip
#upip.install("micropython-umqtt.robust", "/lib")
#upip.install("micropython-umqtt.simple", "/lib")


import network
import utime
import ussl
from umqtt.simple import MQTTClient
from machine import Pin
import secrets

ssid = secrets.ssid
wifipsw = secrets.wifipsw
broker = secrets.broker

with open("ca.crt.der", 'rb') as f:
    cert = f.read()

ssl_params = {'cert': cert}

def connectMQTT():
    client = MQTTClient(client_id=b"frenchie_rasp_picow",
                        server=broker,
                        port=1883,
                        keepalive=60)#,
                        #ssl=True,
                        #ssl_params=ssl_params
                        #)
    client.connect()
    return client

def publish():
    client.publish("plugToggle","toggle")
    print("publish Done")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid,wifipsw)
while True:
    if wlan.status() < 0 or wlan.status() >= 3:
        print(wlan.ifconfig()[0])
        break
    print('waiting for connection...')
    utime.sleep(1)
 

client = connectMQTT()
publish()


