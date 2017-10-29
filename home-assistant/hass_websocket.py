#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides a lightweight connection to home-assistant websocket.

Usage:
import hass_websocket
hass = hass_websocket.HassWebsocket("192.168.123.123")
hass.ws_connect()
hass.volume_down("receiver_living_room")
hass.volume_down("receiver_living_room")

:copyright: (c) 2017 by Oliver Goetz.
:license: MIT, see LICENSE for more details.
"""
import json

# uses https://pypi.python.org/pypi/websocket-client
import websocket


class HassWebsocket(object):
    """Lightweight connector to HASS websocket interface."""
    def __init__(self, host, timeout=2.0, api_passwd=None):
        # Host name and API passwd of hass
        self._host = host
        self._api_passwd = api_passwd
        # Websocket message ID counter
        self._msg_id = 0

        # Create websocket connection
        websocket.enableTrace(False)
        self._ws = websocket.WebSocket(enable_multithread=True)
        # Set timeout for the connection
        self._ws.settimeout(timeout)

    def ws_connect(self, reconnect=False):
        if reconnect:
            # close connection first when reconnecting
            self._ws.close()

        # connect to socket
        self._ws.connect('ws://{}:8123/api/websocket'.format(self._host))
        if self._api_passwd:
            # create authentication message
            ws_msg_dict = {'type': 'auth',
                           'api_password': self._api_passwd}
            ws_msg = json.dumps(ws_msg_dict)
            # Send authentication message
            self._ws_send(ws_msg)
        # Reset message ID
        self._msg_id = 0

    def _ws_send(self, ws_message):
        # Send to socket
        try:
            self._ws.send(ws_message)
        except (IOError,
                websocket.WebSocketTimeoutException,
                websocket.WebSocketConnectionClosedException):
            # Restart connection on connection loss
            self.ws_connect(reconnect=True)
            try:
                self._ws.send(ws_message)
            except (IOError,
                    websocket.WebSocketTimeoutException,
                    websocket.WebSocketConnectionClosedException):
                return False

        # Increase message ID
        self._msg_id += 1
        return True

    def volume_down(self, media_player):
        ws_msg_dict = {'id': self._msg_id,
                       'type': 'call_service',
                       'domain': 'media_player',
                       'service': 'volume_down',
                       'service_data': {
                           'entity_id': 'media_player.{}'.format(media_player)}
                       }

        # Create message in json format
        ws_msg = json.dumps(ws_msg_dict)

        # Send and return
        return(self._ws_send(ws_msg))

    def volume_up(self, media_player):
        ws_msg_dict = {'id': self._msg_id,
                       'type': 'call_service',
                       'domain': 'media_player',
                       'service': 'volume_up',
                       'service_data': {
                           'entity_id': 'media_player.{}'.format(media_player)}
                       }

        # Create message in json format
        ws_msg = json.dumps(ws_msg_dict)

        return(self._ws_send(ws_msg))
