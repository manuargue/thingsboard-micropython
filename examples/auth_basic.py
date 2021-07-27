# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

from uthingsboard.client import TBDeviceMqttClient


def main():
    # Basic auth with user and password
    credentials = {'user': 'myuser', 'password': 'mypassword'}

    # Basic auth with user only
    # credentials = {'user': 'myuser'}

    # Basic auth with Client ID only
    # credentials = {'client_id': 'myclient'}

    # Basic auth with all fields:
    # credentials = {'user': 'myuser', 'password': 'mypassword',
    #                'client_id': 'myclient'}

    client = TBDeviceMqttClient('127.0.0.1', basic_auth=credentials)
    client.connect()
    client.disconnect()


if __name__ == '__main__':
    main()
