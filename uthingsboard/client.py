# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

import json
import sys

from umqtt.robust import MQTTClient


RPC_RESPONSE_TOPIC = 'v1/devices/me/rpc/response/'
RPC_REQUEST_TOPIC = 'v1/devices/me/rpc/request/'
ATTRIBUTES_TOPIC = 'v1/devices/me/attributes'
ATTRIBUTES_TOPIC_REQUEST = 'v1/devices/me/attributes/request/'
ATTRIBUTES_TOPIC_RESPONSE = 'v1/devices/me/attributes/response/'
TELEMETRY_TOPIC = 'v1/devices/me/telemetry'
CLAIMING_TOPIC = 'v1/devices/me/claim'
PROVISION_TOPIC_REQUEST = '/provision/request'
PROVISION_TOPIC_RESPONSE = '/provision/response'


class TBQoSException(Exception):
    pass


class TBAuthException(Exception):
    pass


def validate_qos(qos):
    if qos not in (0, 1):
        raise TBQoSException('Quality of service (qos) value must be 0 or 1')


class TBDeviceMqttClient:

    DEBUG = False

    def __init__(self, host, port=1883, access_token=None, basic_auth=None,
                 keepalive=0, ssl_params=None, qos=0):
        validate_qos(qos)

        # validate authentication
        if access_token and basic_auth:
            raise TBAuthException('Only one auth method must be provided')
        elif access_token:
            user = access_token
            password = client_id = ''
        elif basic_auth:
            valid_keys = ('user', 'password', 'client_id')
            if not all(k in valid_keys for k in basic_auth.keys()):
                raise TBAuthException('valid keys are {}'.format(valid_keys))
            elif basic_auth.get('password') and not basic_auth.get('user'):
                raise TBAuthException('user must be provided')
            elif not basic_auth.get('user') and not basic_auth.get('client_id'):
                raise TBAuthException('client_id or user must be provided')
            user = basic_auth.get('user', '')
            password = basic_auth.get('password', '')
            client_id = basic_auth.get('client_id', '')
        else:
            raise TBAuthException('At least one auth method must be provided')

        ssl_params = ssl_params if ssl_params else {}
        self._client = MQTTClient(client_id, host, port=port, user=user,
                                  password=password, keepalive=keepalive,
                                  ssl=bool(ssl_params), ssl_params=ssl_params)

        self._qos = qos
        self._is_connected = False
        self._attr_request_dict = {}
        self._device_on_server_side_rpc_response = None
        self._device_max_sub_id = 0
        self._device_client_rpc_number = 0
        self._device_sub_dict = {}
        self._device_client_rpc_dict = {}
        self._attr_request_number = 0
        self._client.set_callback(self._on_message)

    def is_connected(self):
        return self._is_connected

    def connect(self):
        if self._is_connected:
            return 0

        ret = self._client.connect()
        if ret == 0:
            self._log('Connected to ThingsBoard')
            self._is_connected = True
            self._log('Subscribing to attributes and RPC topics')
            self._client.subscribe(ATTRIBUTES_TOPIC, qos=self._qos)
            self._client.subscribe(ATTRIBUTES_TOPIC + '/response/+',
                                   qos=self._qos)
            self._client.subscribe(RPC_REQUEST_TOPIC + '+', qos=self._qos)
            self._client.subscribe(RPC_RESPONSE_TOPIC + '+', qos=self._qos)
        return ret

    def reconnect(self):
        self._log('Reconnecting to ThingsBoard')
        return self._client.reconnect()

    def disconnect(self):
        if self._is_connected:
            self._log('Disconnecting from ThingsBoard')
            self._client.disconnect()
            self._is_connected = False

    def wait_msg(self):
        return self._client.wait_msg()

    def check_msg(self):
        return self._client.check_msg()

    def claim(self, secret_key, duration=30000):
        claiming_request = {
            'secretKey': secret_key,
            'durationMs': duration
        }
        self._client.publish(CLAIMING_TOPIC, json.dumps(
            claiming_request), qos=self._qos)

    def send_rpc_reply(self, req_id, resp, qos=0):
        validate_qos(qos)
        self._client.publish(RPC_RESPONSE_TOPIC + req_id, resp, qos=qos)

    def send_rpc_call(self, method, params, callback):
        self._device_client_rpc_number += 1
        self._device_client_rpc_dict.update(
            {self._device_client_rpc_number: callback})
        rpc_request_id = self._device_client_rpc_number
        payload = {'method': method, 'params': params}
        self._client.publish(RPC_REQUEST_TOPIC + str(rpc_request_id),
                             json.dumps(payload),
                             qos=self._qos)

    def set_server_side_rpc_request_handler(self, handler):
        # handler signature is callback(req_id, method, params)
        self._device_on_server_side_rpc_response = handler

    def publish_data(self, topic, data, qos=0):
        validate_qos(qos)
        self._client.publish(topic, json.dumps(data), qos=qos)

    def send_telemetry(self, telemetry, qos=0):
        if not isinstance(telemetry, list):
            telemetry = [telemetry]
        return self.publish_data(TELEMETRY_TOPIC, telemetry, qos=qos)

    def send_attributes(self, attributes, qos=0):
        # attributes is a string or a list of strings
        return self.publish_data(ATTRIBUTES_TOPIC, attributes, qos=qos)

    def unsubscribe_from_attribute(self, subscription_id):
        for attribute in self._device_sub_dict:
            if self._device_sub_dict[attribute].get(subscription_id):
                del self._device_sub_dict[attribute][subscription_id]
                self._log('Unsubscribed from %s, subscription id %i',
                          attribute, subscription_id)
        if subscription_id == '*':
            self._device_sub_dict = {}
        self._device_sub_dict = dict(
            (k, v) for k, v in self._device_sub_dict.items() if v)

    def subscribe_to_all_attributes(self, callback):
        # callback signature is callback(attributes)
        return self.subscribe_to_attribute('*', callback)

    def subscribe_to_attribute(self, key, callback):
        # callback signature is callback(attributes)
        self._device_max_sub_id += 1
        if key not in self._device_sub_dict:
            self._device_sub_dict.update(
                {key: {self._device_max_sub_id: callback}})
        else:
            self._device_sub_dict[key].update(
                {self._device_max_sub_id: callback})
        self._log('Subscribed to %s with id %i', key, self._device_max_sub_id)
        return self._device_max_sub_id

    def request_attributes(self, client_keys=None, shared_keys=None,
                           callback=None):
        # callback signature is callback(resp_id, attributes)
        if client_keys is None and shared_keys is None:
            self._log('There are no keys to request')
            return False

        msg = {}
        if client_keys:
            msg.update({'clientKeys': ','.join(client_keys)})
        if shared_keys:
            msg.update({'sharedKeys': ','.join(shared_keys)})

        req_id = self._add_attr_request_callback(callback)
        self._client.publish(ATTRIBUTES_TOPIC_REQUEST + str(req_id),
                             json.dumps(msg),
                             qos=self._qos)
        return True

    def _add_attr_request_callback(self, callback):
        self._attr_request_number += 1
        self._attr_request_dict.update({self._attr_request_number: callback})
        return self._attr_request_number

    def _on_message(self, topic, msg):
        topic = topic.decode('utf-8')
        payload = json.loads(msg.decode('utf-8'))
        self._log('Rx on {}: {}'.format(topic, payload))
        self._on_decoded_message(topic, payload)

    def _on_decoded_message(self, topic, payload):
        if topic.startswith(RPC_REQUEST_TOPIC):
            req_id = topic[len(RPC_REQUEST_TOPIC):]
            if self._device_on_server_side_rpc_response:
                method = payload.get('method')
                params = payload.get('params')
                self._device_on_server_side_rpc_response(req_id, method,
                                                         params)
        elif topic.startswith(RPC_RESPONSE_TOPIC):
            resp_id = int(topic[len(RPC_RESPONSE_TOPIC):])
            callback = self._device_client_rpc_dict.pop(resp_id)
            if callback:
                callback(resp_id, payload)
        elif topic == ATTRIBUTES_TOPIC:
            callbacks = []
            # callbacks for everything
            if self._device_sub_dict.get('*'):
                for subscription_id in self._device_sub_dict['*']:
                    callbacks.append(
                        self._device_sub_dict['*'][subscription_id])
            # specific callback, iterate through message
            for key in payload.keys():
                # find key in our dict
                if self._device_sub_dict.get(key):
                    for subscription in self._device_sub_dict[key]:
                        callbacks.append(
                            self._device_sub_dict[key][subscription])
            for cb in callbacks:
                cb(payload)
        elif topic.startswith(ATTRIBUTES_TOPIC_RESPONSE):
            resp_id = int(topic[len(ATTRIBUTES_TOPIC + '/response/'):])
            callback = self._attr_request_dict.pop(resp_id)
            if callback:
                callback(payload)

    def _log(self, msg, *args):
        if self.DEBUG:
            stream = sys.stderr.write('%s:%s:' % (self.__name__))
            if not args:
                print(msg, file=stream)
            else:
                print(msg % args, file=stream)
