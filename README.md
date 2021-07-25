# ThingsBoard MQTT MicroPython client

This project is a MicroPython library that provides an client for the [Device](https://thingsboard.io/docs/reference/mqtt-api/) API of [ThingsBoard](https://thingsboard.io/) open-source IoT Platform.

The library consists of a thin wrapper around the MicroPython MQTT module, [mqtt.robust](https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/umqtt/robust.py).

## Installation

To install using pip:

```python
import upip
upip.install('thingsboard-micropython')
```

## Getting Started

Client initialization and telemetry publishing:

```python
from uthingsboard.client import TBDeviceMqttClient

client = TBDeviceMqttClient('test01', '127.0.0.1', user='test01', password='test01')

# Connect to ThingsBoard
client.connect()

# Sending telemetry
telemetry = {'temperature': 41.9, 'enabled': False}
client.send_telemetry(telemetry)

# Checking for incoming subscriptions or RPC call requests (non-blocking)
client.check_msg()

# Disconnect from ThingsBoard
client.disconnect()
```

## Examples

More examples can be found in [examples](https://github.com/coredumplabs/thingsboard-micropython/tree/main/examples) directory.

## Support

- QoS 0 and 1 as supported by the backend MQTT library, [mqtt.robust](https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/umqtt/robust.py).
- All [Device](https://thingsboard.io/docs/reference/mqtt-api/), except Provisioning.
- Tested only on ESP32 board running MicroPython v1.16 generic.

## Acknowledgment

This library is an adapted version of the official [ThingsBoard client SDK for Python](https://github.com/thingsboard/thingsboard-python-client-sdk),
to run in MicroPython.

## License

This project is released under [Apache 2.0 License](https://github.com/coredumplabs/thingsboard-micropython/tree/main/LICENSE).
