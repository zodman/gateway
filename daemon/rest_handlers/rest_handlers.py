import tornado.web
import json
import random
import logging
from tornado.web import asynchronous, HTTPError

def random_id_number():
    return random.randint(0, 2**32 - 1)

# Implements the on_fetch method for all HTTP requests.
class BaseHTTPHandler(tornado.web.RequestHandler):


    def success_response(self, data):
        return {
            'status':'success',
            'data': data
            }

    def _callback_response(self, *args,**kwargs):
        success, data_response = args
        data = { 'height': data_response }
        if not success:
            response_dict = self.success_response(data)
        self.write(json.dumps(response_dict))
        self.finish()

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

        logging.info("handle to obelisk")
        self.application.client.fetch_history(address, self._end)

    def _end(self,ec,history):
        logging.info("fetch_history %s %s", ec,history )
        res  =  ec, history
        self.write(json.dumps(res))
        self.finish()

class HeightHandler(BaseHTTPHandler):

    @asynchronous
    def get(self):
        self.application.client.fetch_last_height(self._callback_response)

