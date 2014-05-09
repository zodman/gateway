import tornado.web
import json
import base58
import random
import logging
from tornado.web import asynchronous, HTTPError

def random_id_number():
    return random.randint(0, 2**32 - 1)

# Implements the on_fetch method for all HTTP requests.
class BaseHTTPHandler(tornado.web.RequestHandler):

    def queue_response(self, response):
        logging.info("response %s", response)
        self.finish(json.dumps(response))

class BlockHeaderHandler(BaseHTTPHandler):

    def _get_request(self, args):
        return  {
            "id": random_id_number(),
            "command":"fetch_block_header",
            "params": args
        }

    @asynchronous
    def get(self, blk_hex=None):
        if blk_hex is None:
            raise HTTPError(400, reason="No block hash")
        blk_hash = blk_hex.decode("hex")
        request = self._get_request([blk_hash])
        self.application.obelisk_handler.handle_request(self, request)


class BlockTransactionsHandler(BlockHeaderHandler):

        def _get_request(self, args):
            return {
                "id": random_id_number(),
                "command":"fetch_block_transaction_hashes",
                "params": args
            }


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

        self.application.obelisk_handler.handle_request(self, request)

class AddressHistoryHandler(BaseHTTPHandler):
    @asynchronous
    def get(self, address=None):
        if address is None:
            raise HTTPError(400, reason="No address")

        try:
            from_height = long(self.get_argument("from_height", 0))
        except ValueError:
            raise HTTPError(400, reason="Invalid height")

        request = {
            "id": random_id_number(),
            "command":"fetch_history",
            "params": [address, from_height]
        }

        self.application.obelisk_handler.handle_request(self, request)

class HeightHandler(BaseHTTPHandler):
    @asynchronous
    def get(self):
        request = {
            "id": random_id_number(),
            "command":"fetch_last_height",
            "params": []
        }

        self.application.obelisk_handler.handle_request(self, request)

