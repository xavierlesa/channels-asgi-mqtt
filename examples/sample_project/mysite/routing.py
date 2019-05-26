# mysite/routing.py

from channels.routing import ProtocolTypeRouter, ChannelNameRouter
from mqtt_app.consumers import MqttConsumer

application = ProtocolTypeRouter({
    "channel": ChannelNameRouter({
        "mqtt": MqttConsumer
    }),
})
