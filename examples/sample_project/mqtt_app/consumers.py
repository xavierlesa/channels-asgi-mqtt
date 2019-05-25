from channels.consumer import SyncConsumer


class MqttConsumer(SyncConsumer):

    def mqtt_sub(self, event):
        topic = event['text']['topic']
        payload = event['text']['payload']
        # do something with topic and payload

    def mqtt_pub(self,event):
        pass
