import sys
import importlib
import argparse
import logging

from .server import Server


logger = logging.getLogger(__name__)


def channel_type(channel_name):
    sys.path.insert(0, ".")
    module_path, object_path = channel_name.split(":", 1)
    channel_layer = importlib.import_module(module_path)
    for bit in object_path.split("."):
        channel_layer = getattr(channel_layer, bit)

    return channel_layer


def main():
    parser = argparse.ArgumentParser(description="Interface between MQTT and ASGI and Channels 2.0 compatible")
    parser.add_argument("-H", "--host", help="MQTT broker host",
                        default="localhost")
    parser.add_argument("-p", "--port", help="MQTT broker port", type=int,
                        default=1883)
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="Set verbosity")
    parser.add_argument("channel_layer",
                        help=("The ASGI channel layer instance to use as "
                              "path.to.module:instance.path"))
    parser.add_argument("-U", "--username", help="MQTT username to authorised connection")
    parser.add_argument("-P", "--password", help="MQTT password to authorised connection")
    parser.add_argument("-i", "--id", dest="client_id", help="MQTT Cliente ID")

    parser.add_argument("--topic", action="append", dest="topics",
            help="MQTT topics with qos to subscribe \
                    --topic TOPIC:QOS \
                    --topic /office/sensor:0 --topic /home/sensor:1 \
                    If empty (#, 2) is set as default")

    parser.add_argument("-n", "--channel-name",
            help="Name of Channels's channel to send and receive messages")

    parser.add_argument("-s", "--channel-sub",
            help="Name of Channels's channel for MQTT Sub messages, default is mqtt.pub")

    parser.add_argument("-x", "--channel-pub",
            help="Name of Channels's channel for MQTT Pub messages, default is mqtt.sub")

    args = parser.parse_args()
 
    logging.basicConfig(
        level={
            0: logging.WARN,
            1: logging.INFO,
            2: logging.DEBUG,
        }.get(args.verbosity, logging.DEBUG),
        format="%(asctime)-15s %(levelname)-8s %(message)s",
    )

    channel_layer = channel_type(args.channel_layer)
    topics = []
    if args.topics:
        for t in args.topics:
            topic, qos = t.split(':')
            topics.append((topic, int(qos)))


    logger.info("\r\nStarting interface to MQTT broker {}:{}, channel {}\r\n\
            Topics: {}\r\n\
            MQTT channel name: {}\r\n\
            MQTT SUB: {}\r\n\
            MQTT PUB: {}\r\n".format(
                args.host, args.port, args.channel_layer,
                "\r\n".join(["{}, qos:{}".format(*t) for t in topics]),
                args.channel_name,
                args.channel_sub,
                args.channel_pub,
    ))


    server = Server(
            channel_layer, 
            args.host, 
            args.port, 
            args.username, 
            args.password,
            args.client_id,
            topics_subscription=topics, 
            mqtt_channel_name=args.channel_name, 
            mqtt_channel_sub=args.channel_sub, 
            mqtt_channel_pub=args.channel_pub
        )

    server.run()
