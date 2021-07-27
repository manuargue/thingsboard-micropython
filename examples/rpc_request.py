# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

from uthingsboard.client import TBDeviceMqttClient


def callback(resp_id, data):
    print('Response {id}: {data})'.format(id=resp_id, data=data))


def main():
    client = TBDeviceMqttClient('127.0.0.1', access_token='test01')
    client.connect()

    # call "getTime" on server and receive result, then process it on callback
    client.send_rpc_call('getTime', {}, callback)
    client.wait_msg()

    client.disconnect()


if __name__ == '__main__':
    main()
