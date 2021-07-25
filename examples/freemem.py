# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

import gc
import time

from uthingsboard.client import TBDeviceMqttClient


telemetry_interval = 5
client = TBDeviceMqttClient('test01', '127.0.0.1')


# this callback changes global variable defining how often telemetry is sent
def on_telemetry_interval_change(value):
    global telemetry_interval
    if 'telemetryInterval' in value:
        telemetry_interval = int(value['telemetryInterval'])
    elif 'shared' in value and 'telemetryInterval' in value['shared']:
        telemetry_interval = int(value['shared']['telemetryInterval'])


# this callback handles RPC requests from server
def handle_rpc_request(request_id, method, params):
    print('Request ID {req}: {method}({params})'.format(req=request_id,
                                                        method=method,
                                                        params=params))
    if method == 'getFreeMemory':
        client.send_rpc_reply(request_id, {'memFree': gc.mem_free()})


def main():
    client.set_server_side_rpc_request_handler(handle_rpc_request)
    client.connect()

    # subscribe to future changes of upload frequency
    client.subscribe_to_attribute('telemetryInterval',
                                  on_telemetry_interval_change)

    # fetch the latest setting for upload frequency configured on the server
    client.request_attributes(shared_keys=['telemetryInterval'],
                              callback=on_telemetry_interval_change)

    while True:
        client.send_telemetry({'getFreeMemory': gc.mem_free()})
        client.check_msg()
        time.sleep(telemetry_interval)


if __name__ == '__main__':
    main()
