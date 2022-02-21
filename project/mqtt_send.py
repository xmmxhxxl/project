# python3.6

import json
import random

from paho.mqtt import client as mqtt_client


class MQTTReceive():
    broker = 'www.xmxhxl.top'
    port = 1883
    client_id = f'python-mqtt-{random.randint(0, 1000)}'

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def subscribe(self, client: mqtt_client, topic):
        def on_message(client, userdata, msg):
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            data = json.loads(msg.payload.decode())
            if msg.topic == 'user/openId':
                print(data['openId'])
                print(data['nickName'])
                print(data['avatarUrl'])
            else:
                print(data['msg'])

        client.subscribe(topic)
        client.on_message = on_message

    def run(self, topic):
        client = self.connect_mqtt()
        self.subscribe(client, topic)
        client.loop_forever()


if __name__ == '__main__':
    mqtt = MQTTReceive()
    mqtt.run(topic='user/#')
    # mqtt.run(topic='user/openId')
