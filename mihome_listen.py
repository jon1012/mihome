__author__ = 'lxl'
#!/usr/bin/python
# -*- coding: utf-8 -*-

from connector import *
import ConfigParser
import paho.mqtt.client as mqtt
import json
import sys
import thread
from Crypto.Cipher import AES
import binascii
reload(sys)
sys.setdefaultencoding('utf-8')

subscribed_channels = set()
published_channels = set()

IV = bytearray([0x17, 0x99, 0x6d, 0x09, 0x3d, 0x28, 0xdd, 0xb3, 0xba, 0x69, 0x5a, 0x2e, 0x6f, 0x58, 0x56, 0x2e])


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("xiaomi/test")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print "Topic: ", msg.topic+'\nMessage: '+str(msg.payload)
    items = msg.topic.split('/')
    device_model = items[1]
    device_name = items[2]
    sid = items[3]
    device_channel = items[4]
    gateway_address = userdata[1][sid]['gateway_address']
    token = userdata[0][userdata[1][sid]['gateway_sid']]

    print userdata[2]
    print type(userdata[2])
    user_key = userdata[2][str(gateway_address)]

    print "userkey:", user_key

    aes = AES.new(user_key, AES.MODE_CBC, str(IV))

    ciphertext = aes.encrypt(token)

    write_key = binascii.hexlify(ciphertext)
    if msg.payload == "1":
        command = "on"
    elif msg.payload == "0":
        command = "off"
    else:
        command = "unknown"

    write_command = {"cmd":"write",
                     "model":device_model,
                     "sid":sid,
                     "short_id":4343,
                     "data":{device_channel:command,"key":write_key}}
    userdata[3].send_command(write_command, gateway_address, 9898)
    print write_command




def prepare_mqtt(MQTT_SERVER, MQTT_PORT=1883):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    return client

def push_data(client, model, sid, cmd, data, id2name, PATH_FMT):
    for key, value in data.items():
        if sid in id2name:
            dname = id2name[sid].decode('utf8')
        else:
            dname = sid
        path = PATH_FMT.format(model=model,
                             name=dname,
                             sid=sid,
                             cmd=cmd,
                             prop=key)

        client.publish(path, payload=value.upper(), qos=0)
        if path not in published_channels:
            print "Published to: ", path
            published_channels.add(path)

        if model in ['plug', 'ctrl_neutral2', 'ctrl_neutral1']:
            if path in subscribed_channels:
                pass
            else:
                print "Subscribe to", path + "/command"
                client.subscribe(path + "/command")
                subscribed_channels.add(path)

def ConfigSectionMap(Config, section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1



if __name__ == "__main__":
    id2name = dict()
    Config = ConfigParser.ConfigParser()
    Config.read("mihome_listen.ini")
    MQTT_SERVER = ConfigSectionMap(Config, "MQTT")['server']
    MQTT_PORT = ConfigSectionMap(Config, "MQTT")['port']
    PATH_FMT =  ConfigSectionMap(Config, "MQTT")['mqtt_path']
    devices = ConfigSectionMap(Config, "devices")['sub_devices']

    user_key = Config._sections['user_key']
    data = json.loads(devices.decode('utf-8'))
    for i in data:
        id2name[i['did'].split('.')[1]] = i['name']
    client = prepare_mqtt(MQTT_SERVER, MQTT_PORT)
    #model, sid, cmd, data, gateway
    cb = lambda m, s, c, d: push_data(client, m, s, c, d, id2name, PATH_FMT)
    connector = XiaomiConnector(data_callback=cb)
    node_list = connector.get_nodes()
    #print node_list
    #p = connector.send_whois()

    for node in node_list:
        if node_list[node]["model"] == "gateway":
            pass
        else:
            connector.request_current_status(node, node_list[node]['gateway_address'])
    try:
        thread.start_new_thread(client.loop_forever, ())

    except:
        print "Error: unable to start thread"
    print "start listenning"
    while True:
        connector.check_incoming()

        client.user_data_set((connector.get_token(),node_list,user_key,connector))
        #print connector.get_token()