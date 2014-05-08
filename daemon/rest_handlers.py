import tornado.web
import json
import random
import logging
from tornado.web import asynchronous, HTTPError

def random_id_number():
    return random.randint(0, 2**32 - 1)

# Implements the on_fetch method for all HTTP requests.
class BaseHTTPHandler(tornado.web.RequestHandler):

    def _send_response(self, response):
        try:
            self.write(json.dumps(response))
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



class BlockHeaderHandler(tornado.web.RequestHandler):
    @asynchronous
    def get(self, blk_hash=None):
        if blk_hash is None:
            raise HTTPError(400, reason="No block hash")

        try:
            blk_hash = blk_hash.decode("hex")
        except ValueError:
            raise HTTPError(400, reason="Invalid hash")

        request = {
            "id": random_id_number(),
            "command":"fetch_block_header",
            "params": [blk_hash]
        }

        self.application._obelisk_handler.handle_request(self, request)


class BlockTransactionsHandler(tornado.web.RequestHandler):
    @asynchronous
    def get(self, blk_hash=None):
        if blk_hash is None:
            raise HTTPError(400, reason="No block hash")

        try:
            blk_hash = blk_hash.decode("hex")
        except ValueError:
            raise HTTPError(400, reason="Invalid hash")

        request = {
            "id": random_id_number(),
            "command":"fetch_block_transaction_hashes",
            "params": [blk_hash]
        }

        self.application._obelisk_handler.handle_request(self, request)

class TransactionPoolHandler(tornado.web.RequestHandler):
    @asynchronous
    # Dump transaction pool to user
    def get(self):
        raise NotImplementedError

    def on_fetch(self, ec, pool):
        raise NotImplementedError

    # Send tx if it is valid,
    # validate if ?validate is in url...
    def post(self):
        raise NotImplementedError


class TransactionHandler(tornado.web.RequestHandler):
    @asynchronous
    def get(self, tx_hash=None):
        if tx_hash is None:
            raise HTTPError(400, reason="No block hash")

        try:
            tx_hash = tx_hash.decode("hex")
        except ValueError:
            raise HTTPError(400, reason="Invalid hash")

        request = {
            "id": random_id_number(),
            "command":"fetch_transaction",
            "params": [tx_hash]
        }

        self.application._obelisk_handler.handle_request(self, request)

class AddressHistoryHandler(BaseHTTPHandler):
    @asynchronous
    def get(self, address=None):
        if address is None:
            raise HTTPError(400, reason="No address")

        try:
            from_height = long(self.get_argument("from_height", 0))
        except ValueError:
            raise HTTPError(400)

        request = {
            "id": random_id_number(),
            "command":"fetch_history",
            "params": [address, from_height]
        }
        logging.info("handle to obelisk")
        self.application.obelisk_handler.handle_request(self, request)




class BaseHTTPHandler(tornado.web.RequestHandler):
    def on_fetch(self, response):
        self.finish(response)


class HeightHandler(BaseHTTPHandler):
    @asynchronous
    def get(self):
        request = {
            "id": random_id_number(),
            "command":"fetch_last_height",
            "params": None
        }

        self.application._obelisk_handler.handle_request(self, request)

