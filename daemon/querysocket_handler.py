import tornado
import logging
import threading
from collections import defaultdict
import json


class QuerySocketHandler(tornado.websocket.WebSocketHandler):

    # Set of WebsocketHandler
    listeners = set()
    # Protects listeners
    listen_lock = threading.Lock()

    def initialize(self):
        self._obelisk_handler = self.application.obelisk_handler
        self._brc_handler = self.application.brc_handler
        self._json_chan_handler = self.application.json_chan_handler
        self._ticker_handler = self.application.ticker_handler
        self._subscriptions = defaultdict(dict)
        self._connected = False

    def open(self):
        logging.info("OPEN")
        with QuerySocketHandler.listen_lock:
            self.listeners.add(self)
        self._connected = True

    def on_close(self):
        logging.info("CLOSE")
        disconnect_msg = {'command': 'disconnect_client', 'id': 0, 'params': []}
        self._connected = False
        self._obelisk_handler.handle_request(self, disconnect_msg)
        self._json_chan_handler.handle_request(self, disconnect_msg)
        with QuerySocketHandler.listen_lock:
            self.listeners.remove(self)

    def _check_request(self, request):
        return request.has_key("command") and request.has_key("id") and \
            request.has_key("params") and type(request["params"]) == list

    def on_message(self, message):
        try:
            request = json.loads(message)
        except:
            logging.error("Error decoding message: %s", message, exc_info=True)
            return 

        # Check request is correctly formed.
        if not self._check_request(request):
            logging.error("Malformed request: %s", request, exc_info=True)
            return
        # Try different handlers until one accepts request and
        # processes it.
        if self._json_chan_handler.handle_request(self, request):
            return
        if self._obelisk_handler.handle_request(self, request):
            return
        if self._brc_handler.handle_request(self, request):
            return
        if self._ticker_handler.handle_request(self, request):
            return
        logging.warning("Unhandled command. Dropping request: %s",
            request, exc_info=True)

    def _send_response(self, response):
        try:
            self.write_message(json.dumps(response))
        except tornado.websocket.WebSocketClosedError:
            self._connected = False
            logging.warning("Dropping response to closed socket: %s",
               response, exc_info=True)

    def queue_response(self, response):
        ioloop = tornado.ioloop.IOLoop.current()
        try:
            # calling write_message or the socket is not thread safe
            ioloop.add_callback(self._send_response, response)
        except:
            logging.error("Error adding callback", exc_info=True)

