# Sample Project

This project uses the chasgimqtt interface to receive data from an MQTT broker.

Install dependencies:

```console
pip install channels_redis celery
```

Follow the steps below to run it:

1. [enable channel layer](https://channels.readthedocs.io/en/latest/tutorial/part_2.html#enable-a-channel-layer),
   in this example we use Redis as the backing store:
   - run `redis`:
        ```bash
        docker run -p 6379:6379 -d redis:2.8
        ```
   - add the following to `mysite/settings.py`:
     
            ASGI_APPLICATION = 'mysite.routing.application'
            CHANNEL_LAYERS = {
                'default': {
                    'BACKEND': 'channels_redis.core.RedisChannelLayer',
                    'CONFIG': {
                        "hosts": [('127.0.0.1', 6379)],
                    },
                },
            }
1. `mysite/asgi.py` should look like this:

        import os
        import django
        from channels.routing import get_default_application
        from channels.layers import get_channel_layer
        
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
        django.setup()
        
        # Application
        application = get_default_application()
        
        # Layers
        channel_layer = get_channel_layer()
        
1. `mqtt_app/consumers.py` should look like this :

        from channels.consumer import SyncConsumer

        class MqttConsumer(SyncConsumer):
        
            def mqtt_sub(self, event):
                topic = event['text']['topic']
                payload = event['text']['payload']
                # do something with topic and payload
                
            def mqtt_pub(self,event):
                pass

                
1. `mysite/routing.py` :

        from channels.routing import ProtocolTypeRouter, ChannelNameRouter
        from mqtt_app.consumers import MqttConsumer
        
        application = ProtocolTypeRouter({
            'channel': ChannelNameRouter(
                {
                    "mqtt": MqttConsumer
                }
            )
        })

1. setup Django application:

   ```bash
   python manage.py migrate
   ```
   
   and run it:
   
   ```bash
   python manage.py runserver
   ```

1. run `chasgimqtt`:

    ```bash
    chasgimqtt -H iot.eclipse.org -p 1883 --topic=some_topic:2 mysite.asgi:channel_layer
    ```

1. run the [workers](https://channels.readthedocs.io/en/latest/topics/worker.html#worker-and-background-tasks):

    ```bash
    python3 manage.py runworker mqtt
    ```

1. and publish a message:

    ```bash
    mosquitto_pub -h iot.eclipse.org -p 1883 -t some_topic -m 1
    ```
