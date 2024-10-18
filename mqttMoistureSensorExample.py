#import picoWInit
import envHostname
import time
import envSecrets
import machine
import json
from umqtt.simple import MQTTClient
import os

time.sleep(7)
'''
References:
    - Official Documentation: https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery
    - HELPFUL Example: https://core-electronics.com.au/guides/getting-started-with-mqtt-on-raspberry-pi-pico-w-connect-to-the-internet-of-things/
Notes:
    This is an example MQTT device.  Be sure to propogate the envSecrets file
    with the appropriate variables.  This example sets up the device to be discoverable.
    (using config), it provides a switch you can toggle in Home Assistant to turn the onboard
    LED on or off, as well as the current state of the LED (on or off).
'''
#setup the hardware
adc = machine.ADC(33,atten=machine.ADC.ATTN_11DB)
resetCauseNames = ['PWRON_RESET','HARD_RESET','WDT_RESET','DEEPSLEEP_RESET','SOFT_RESET','BROWN_OUT_RESET']
wakeReasons = ['PIN_WAKE','EXT0_WAKE','EXT1_WAKE','TIMER_WAKE','TOUCHPAD_WAKE','ULP_WAKE']
resetCause = next(item for item in resetCauseNames if machine.reset_cause() == getattr(machine, item))

print(resetCause)
# Test the soil meter with a cup of water to get x_max value.  Notice that the
#max value is LOWER than the min value.  Set the x_min value based on what the
#meter reads when its just in the air.  #Use the additional plus/minus value in
#x_min to adjust the reading closer to what a moisture meter says
x_min = 49000 -12000
x_max = 20200
y_min = 0
y_max = 100


def linear_scale(x, x_min, x_max, y_min, y_max):
    """
    Scales a value from one range to another linearly.
    """
    if x >= x_min:
        return 0.0
    if x <= x_max:
        return 100.0
    return round((y_max - y_min) * (x - x_min) / (x_max - x_min) + y_min,1)

mqtt_server = envSecrets.mqtt_host
mqtt_port=envSecrets.mqtt_port
mqtt_discovery_prefix = envSecrets.mqtt_discovery_prefix
mqtt_user=envSecrets.mqtt_user
client_id = envHostname.hostname
#The state tends to be the root of the device
stateTopic = f"{mqtt_discovery_prefix}/sensor/marbleQueenPothosOnaStickd"
#Notice that config is the stateTopic with /config appended to the end
#Use /config to make it discoverable
configTopic = f"{stateTopic}/config"
#You'll use /set when you have something that can be toggled or adjusted
cmd_topic = f"{stateTopic}/set"

#This will run every time a message is found in any subscribed topic by either the .check_msg() or .wait_msg()
def mqtt_subscription_callback(topic, message):
    print (f'Topic {topic.decode()} received message {message.decode()}')  # Debug print out of what was received over MQTT
    if message == b'ON':
        print("LED ON")
        led.value(1)
    elif message == b'OFF':
        print("LED OFF")
        led.value(0)

#picoWInit.connect()
#Setup the MQTTClient
client = MQTTClient(client_id, mqtt_server, mqtt_port, user=mqtt_user,password=envSecrets.mqtt_password,keepalive=60)
#Setup the callback (only needed if you'll be subscribing to something.
#MUST BE SET BEFORE the client connects
client.set_callback(mqtt_subscription_callback)
#Connect to the MQTT host
client.connect()
print('Connected to %s MQTT Broker'%(mqtt_server))
# if resetCause != 'DEEPSLEEP_RESET':
#     try:
#         configMsg = {
#             "device_class":"moisture",
#             "state_topic":stateTopic,
#             "unit_of_measurement":"%",
#             "value_template":"{{ value_json.moisture}}",
#             "unique_id":"hum01ae",
#             "device":{
#                 "identifiers":[
#                     f"{envHostname.hostname}"
#                 ],
#                 "name": f"marbleQueenPothosOnaStick",
#                 "manufacturer": os.uname().sysname,
#                 "model": os.uname().machine,
#                 "sn": "4c:75:25:ee:cb:54"
#                 }
#             }
# 
#         configMsg = json.dumps(configMsg)
#         client.publish(configTopic, configMsg,retain=True)
#         input('Created device and entity')
#         
#     except Exception as e:
#         print('Running exception')
#         client.publish(configTopic, '')
#Get Soil moisture and publish
result = linear_scale(adc.read_u16(), x_min, x_max, y_min, y_max)
print(result)
currentState = {
    "moisture": result}
currentState = json.dumps(currentState)
time.sleep(1)
client.publish(stateTopic, currentState)
time.sleep(3)


machine.deepsleep(86400000)

