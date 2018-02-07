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
    parser = argparse.ArgumentParser(description="Simple MQTT bridge for ASGI")
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

    args = parser.parse_args()
    logging.basicConfig(
        level={
            0: logging.WARN,
            1: logging.INFO,
        }.get(args.verbosity, logging.DEBUG),
        format="%(asctime)-15s %(levelname)-8s %(message)s",
    )
    channel_layer = channel_type(args.channel_layer)
    logger.info("Starting interface to MQTT broker {}:{}, channel {}".format(
        args.host, args.port, args.channel_layer
    ))
    server = Server(channel_layer, args.host, args.port, args.username, args.password)
    server.run()
