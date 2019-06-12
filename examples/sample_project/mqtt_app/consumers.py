import datetime
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer


class MqttConsumer(SyncConsumer):

    def mqtt_sub(self, event):
        topic = event['text']['topic']
        payload = event['text']['payload']
        # do something with topic and payload
        print("topic: {0}, payload: {1}".format(topic, payload))

    def mqtt_pub(self, event):
        topic = event['text']['topic']
        payload = event['text']['payload']
        # do something with topic and payload
        print("topic: {0}, payload: {1}".format(topic, payload))
