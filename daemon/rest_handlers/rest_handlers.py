import tornado.web
import json
import random
import logging
from tornado.web import asynchronous, HTTPError
import obelisk
from obelisk import bitcoin

def random_id_number():
    return random.randint(0, 2**32 - 1)

# Implements the on_fetch method for all HTTP requests.
class BaseHTTPHandler(tornado.web.RequestHandler):
    def send_response(self, response):
        self._response(response)

    def _response(self, response):
        self.write(json.dumps(response))
        self.finish()

    def success_response(self, data):
        return {
            'status':'success',
            'data': data
            }

    def fail_response(self, data):
        return {
            'status':'fail',
            'data': data
        }

    def error_response(self, data):
        return {
            'status':'error',
            'data':data
        }

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
        self.address = address
        self.application.client.fetch_history(address, self._callback_response)

    def _callback_response(self,ec,history):
        logging.info("fetch_history %s %s", ec,history )
        address = {}
        total_balance = 0
        total_balance += sum(row[3] for row in history
                                                 if row[-1] != obelisk.MAX_UINT32)
        _,hash160 = bitcoin.bc_address_to_hash_160(self.address)
        logging.info(" hash160 %s", hash160)
        address.update({'total_balance': total_balance, 
               # 'hash160':hash160.decode("hex"), # bitcoin.bc_address_to_hash_160(self.address),
                'address':self.address})
        data = {'address': address}
        if not ec:
            response = self.success_response(data)
        else:
            response = self.error_response(history)
        self.send_response(response)


class HeightHandler(BaseHTTPHandler):

    @asynchronous
    def get(self):
        self.application.client.fetch_last_height(self._before_callback_response)

    def _before_callback_response(self, ec, height):
        self.height = height
        self.application.client.fetch_block_header(height, self._callback_response)

    def _callback_response(self, ec, header):
        data = { 'last_height': self.height, 'last_header_block': header.encode("hex") }
        response_dict = self.success_response(data)
        self.send_response(response_dict)


