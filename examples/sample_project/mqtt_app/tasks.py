from __future__ import absolute_import, unicode_literals

from celery.schedules import crontab
from celery import shared_task

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

@shared_task(bind=True)
def mqtt_test(self, msg):
    print(f"Celery task say: \"{msg}\"")

    async_to_sync(channel_layer.send)('mqtt', {
        'type': 'mqtt.pub',
        'text': {
            'topic': 'testmq', 
            'payload': f"{msg} - {self.request.id}"
        }
    })
