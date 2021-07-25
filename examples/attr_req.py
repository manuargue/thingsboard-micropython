# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

from uthingsboard.client import TBDeviceMqttClient


def on_attributes_change(data):
    print(data)


def main():
    client = TBDeviceMqttClient('test01', '127.0.0.1')
    client.connect()

    # request attributes, wait for reply and process it in the callback
    client.request_attributes(client_keys=['myAttr1'],
                              shared_keys=['myAttr2', 'myAttr3'],
                              callback=on_attributes_change)
    client.wait_msg()

    client.disconnect()


if __name__ == '__main__':
    main()
