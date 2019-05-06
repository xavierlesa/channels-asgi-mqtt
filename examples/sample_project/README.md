# Sample Project
this project uses chasgimqtt interface to receive data from mqtt broker.
follow the steps below to run it:

1) you need to [enable channel layer](https://channels.readthedocs.io/en/latest/tutorial/part_2.html#enable-a-channel-layer),
   in this example we uses redis as backing store:
   - run `redis`:
        ```bash
        docker run -p 6379:6379 -d redis:2.8
        ```
   - add the following to mysite/setting.py
     
            ASGI_APPLICATION = 'mysite.routing.application'
            CHANNEL_LAYERS = {
                'default': {
                    'BACKEND': 'channels_redis.core.RedisChannelLayer',
                    'CONFIG': {
                        "hosts": [('127.0.0.1', 6379)],
                    },
                },
            }
2) `mysite/asgi.py` should look like this:

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
        
3) `mqtt_app/consumers.py` should look like this :

        from channels.consumer import SyncConsumer

        class MqttConsumer(SyncConsumer):
        
            def mqtt_sub(self, event):
                topic = event['text']['topic']
                payload = event['text']['payload']
                # do something with topic and payload
                
            def mqtt_pub(self,event):
                pass

                
4) `mysite/routing.py` :

        from channels.routing import ProtocolTypeRouter, ChannelNameRouter
        from mqtt_app.consumers import MqttConsumer
        
        application = ProtocolTypeRouter({
            'channel': ChannelNameRouter(
                {
                    "mqtt": MqttConsumer
                }
            )
        })
        
5) run `chasgimqtt`:

    ```bash
    chasgimqtt -H iot.eclipse.org -p 1883 --topic=some_topic:2 your_channel_application.asgi:channel_layer
    ```

6) run the [workers](https://channels.readthedocs.io/en/latest/topics/worker.html#worker-and-background-tasks):

    ```bash
    python3 manage.py runworker mqtt
    ```