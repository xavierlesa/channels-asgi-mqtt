# channels-asgi-mqtt
Interface between MQTT and ASGI and Channels 2.0 compatible


## Installation

```bash
pip install chasgimqtt
```


## Configuration

First you would to configure a valid `channel_layer` endpoint to consume and connect between chasgimqtt and channels.

In `your_channel_application/asgi.py`:

```python
import os
import django
from channels.routing import get_default_application
from channels.layers import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_channel_application.settings")
django.setup()

# Application
application = get_default_application()

# Layers
channel_layer = get_channel_layer()
```


## Usage

```bash
chasgimqtt -H iot.eclipse.org -p 1883 --topic=some_topic:2 your_channel_application.asgi:channel_layer
```


## Options

```
chasgimqtt -h

usage: chasgimqtt [-h] [-H HOST] [-p PORT] [-v] [-U USERNAME] [-P PASSWORD]
                  [--topic TOPICS] [-n CHANNEL_NAME] [-s CHANNEL_SUB]
                  [-x CHANNEL_PUB]
                  channel_layer

Simple MQTT bridge for ASGI

positional arguments:
  channel_layer         The ASGI channel layer instance to use as
                        path.to.module:instance.path

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  MQTT broker host
  -p PORT, --port PORT  MQTT broker port
  -v, --verbosity       Set verbosity
  -U USERNAME, --username USERNAME
                        MQTT username to authorised connection
  -P PASSWORD, --password PASSWORD
                        MQTT password to authorised connection
  --topic TOPICS        MQTT topics with qos to subscribe --topic TOPIC:QOS
                        --topic /office/sensor:0 --topic /home/sensor:1 If
                        empty (#, 2) is set as default
  -n CHANNEL_NAME, --channel-name CHANNEL_NAME
                        Name of Channels's channel to send and receive
                        messages
  -s CHANNEL_SUB, --channel-sub CHANNEL_SUB
                        Name of Channels's channel for MQTT Sub messages,
                        default is mqtt.pub
  -x CHANNEL_PUB, --channel-pub CHANNEL_PUB
                        Name of Channels's channel for MQTT Pub messages,
                        default is mqtt.sub
```


**HOST**: MQTT broker host

**PORT**: MQTT broker port, default 1883

**USERNAME**: MQTT username to authorised connection

**PASSWORD**: MQTT password to authorised connection

**TOPICS**: MQTT topics with qos to subscribe. This option expect a valid topic name and a QOS value splited by `:`

To subscribe to a list of topics use the same option `--topic`.

```
--topic some_topic:qos --topic another_topic:qos --topic home/kitchen_gas_sensor:2 --topic home/office_air_sensor:0
```

**CHANNEL_NAME** : Name of Channels's channel to send and receive messages, this `channel_name` must to exist in your channel's consumer, default is `mqtt`.

**CHANNEL_SUB** : Name of Channels's channel for MQTT Sub messages, default is `mqtt.sub`.

**CHANNEL_PUB** : Name of Channels's channel for MQTT Pub messages, default is `mqtt.pub`.

