import os
import asyncio
import functools
import logging
import time
import signal
import json

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

async def mqtt_send(future, channel_layer, channel, event):
    result = await channel_layer.send(channel, event)
    future.set_result(result)

async def mqtt_group_send(future, channel_layer, group, event):
    result  = await channel_layer.group_send(group, event)
    future.set_result(result)

# Solo para grupos
async def mqtt_group_add(future, channel_layer, group):
    channel_layer.channel_name = channel_layer.channel_name or await channel_layer.new_channel()
    result = await channel_layer.group_add(group, channel_layer.channel_name)
    future.set_result(result)

# Solo para grupos
async def mqtt_group_discard(future, channel_layer, group):
    result = await channel_layer.group_discard(group, channel_layer.channel_name)
    future.set_result(result)


class Server(object):
    def __init__(self, channel, host, port, username=None, password=None, 
            client_id=None, topics_subscription=None, mqtt_channel_name = None, 
            mqtt_channel_sub=None, mqtt_channel_pub=None):

        self.channel = channel
        self.host = host
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(client_id=self.client_id, userdata={
            "server": self,
            "channel": self.channel,
            "host": self.host,
            "port": self.port,
        })
        self.username = username
        self.password = password
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.topics_subscription = topics_subscription or [("#", 2),]
        assert isinstance(self.topics_subscription, list), "Topic subscription must be a list with (topic, qos)"

        self.mqtt_channel_name = mqtt_channel_name or "mqtt"
        self.mqtt_channel_pub = mqtt_channel_pub or "mqtt.pub"
        self.mqtt_channel_sub = mqtt_channel_sub or "mqtt.sub"


    def _on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with status {}".format(rc))
        client.subscribe(self.topics_subscription)


    def _on_disconnect(self, client, userdata, rc):
        logger.info("Disconnected")
        if not self.stop:
            j = 3
            for i in range(j):
                logger.info("Trying to reconnect")
                try:
                    client.reconnect()
                    logger.info("Reconnected")
                    break
                except Exception as e:
                    if i < j:
                        logger.warn(e)
                        time.sleep(1)
                        continue
                    else:
                        raise

    def _mqtt_send_got_result(self, future):
        logger.debug("Sending message to MQTT channel, with result\r\n%s", future.result())

    def _on_message(self, client, userdata, message):
        logger.debug("Received message from topic {}".format(message.topic))
        payload = message.payload.decode("utf-8")

        try:
            payload = json.loads(payload)
        except:
            logger.debug("Payload is nos a JSON Serializable\r\n%s", payload)
            pass

        msg = {
            "topic": message.topic,
            "payload": payload,
            "qos": message.qos,
            "host": userdata["host"],
            "port": userdata["port"],
        }

        try:

            future = asyncio.Future()
            asyncio.ensure_future(
                    mqtt_send(
                        future, 
                        self.channel, 
                        self.mqtt_channel_name,
                        {
                            "type": self.mqtt_channel_sub,
                            "text": msg
                        })
                )

            future.add_done_callback(self._mqtt_send_got_result)

            
        except Exception as e:
            logger.error("Cannot send message {}".format(msg))
            logger.exception(e)


    async def client_pool_start(self):
        # Loop para recibir mensajes MQTT
        if self.username:
            self.client.username_pw_set(username=self.username, password=self.password)
        
        self.client.connect(self.host, self.port)

        logger.info("Starting loop")

        while True:
            self.client.loop(0.1)
            #logger.debug("Restarting loop")
            await asyncio.sleep(0.1)


    def _mqtt_receive(self, msg):
        """
        Recibe un mensaje desde el Channel `mqtt.pub` y lo envia al broker MQTT
        """

        # Solo nos interesan los messages del channel asociado al mqtt_channel_pub
        if msg['type'] == self.mqtt_channel_pub:

            payload = msg['text']

            if not isinstance(payload, dict):
                payload = json.loads(payload)

            logger.info("Recibe un menssage con payload: %s", msg)
            self.client.publish(
                    payload['topic'], 
                    payload['payload'], 
                    qos=payload.get('qos', 2), 
                    retain=False)


    async def client_pool_message(self):
        logger.info("Loop de recepción de messages")

        while True:
            logger.info("Espera recibir un message desde el channel %s", self.mqtt_channel_name)
            result = await self.channel.receive(self.mqtt_channel_name)
            self._mqtt_receive(result)
            await asyncio.sleep(0.1)
            

    def stop_server(self, signum):
        logger.info("Received signal {}, terminating".format(signum))
        self.stop = True
        for task in asyncio.Task.all_tasks():
            task.cancel()
        self.loop.stop()


    def run(self):
        self.stop = False
        loop = asyncio.get_event_loop()
        self.loop = loop

        for signame in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(
                    getattr(signal, signame),
                    functools.partial(self.stop_server, signame)
                )

        print("Event loop running forever, press Ctrl+C to interrupt.")
        print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())


        tasks = asyncio.gather(*[
                asyncio.ensure_future(self.client_pool_start()),
                asyncio.ensure_future(self.client_pool_message()),
            ])

        asyncio.wait(tasks)

        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())            
            loop.close()
        
        self.client.disconnect()
