from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite', broker='redis://')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'msg-every-5-seconds': {
        'task': 'mqtt_app.tasks.mqtt_test',
        'schedule': 5,
        'args': ('hello', )
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
