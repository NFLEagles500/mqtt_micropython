import picoWInit
import envHostname
import time
import envSecrets
import machine
import json
from umqtt.simple import MQTTClient

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
led = machine.Pin("LED", machine.Pin.OUT)

mqtt_server = envSecrets.mqtt_host
mqtt_port=envSecrets.mqtt_port
mqtt_discovery_prefix = envSecrets.mqtt_discovery_prefix
mqtt_user=envSecrets.mqtt_user
client_id = envHostname.hostname
#The state tends to be the root of the device
stateTopic = f"{mqtt_discovery_prefix}/switch/{envSecrets.hostname}"
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

picoWInit.connect()
#Setup the MQTTClient
client = MQTTClient(client_id, mqtt_server, mqtt_port, user=mqtt_user,password=envSecrets.mqtt_password,keepalive=60)
#Setup the callback (only needed if you'll be subscribing to something.
#MUST BE SET BEFORE the client connects
client.set_callback(mqtt_subscription_callback)
#Connect to the MQTT host
client.connect()
print('Connected to %s MQTT Broker'%(mqtt_server))
try:
    configMsg = {
        "name": None,
        "command_topic": cmd_topic,
        "state_topic": stateTopic,
        "unique_id": f"{envSecrets.hostname}_onboardLED",
        "device": {"identifiers": ["onboardLED"], "name": envSecrets.hostname },
        "state_off": 'OFF',
        "state_on": 'ON'
        
        }
    configMsg = json.dumps(configMsg)
    client.publish(configTopic, configMsg)
    client.subscribe(cmd_topic)

    while True:
        client.check_msg()
        if led.value() == 0:
            pubText = 'OFF'
        else:
            pubText = 'ON'

        client.publish(stateTopic,pubText)
        
        time.sleep(2)
except Exception as e:
    client.publish(configTopic, '')
finally:
    client.publish(configTopic, '')


