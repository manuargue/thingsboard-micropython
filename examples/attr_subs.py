# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

from uthingsboard.client import TBDeviceMqttClient


def callback(data):
    print(data)


def main():
    client = TBDeviceMqttClient('test01', '127.0.0.1')
    client.connect()

    sub_id_1 = client.subscribe_to_attribute('uploadFrequency', callback)
    sub_id_2 = client.subscribe_to_all_attributes(callback)

    client.unsubscribe_from_attribute(sub_id_1)
    client.unsubscribe_from_attribute(sub_id_2)

    client.disconnect()


if __name__ == '__main__':
    main()
