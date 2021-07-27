# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

from uthingsboard.client import TBDeviceMqttClient


def main():
    client = TBDeviceMqttClient('127.0.0.1', access_token='test01')
    client.connect()
    client.disconnect()


if __name__ == '__main__':
    main()
