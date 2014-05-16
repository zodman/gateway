import tornado.web
import json
import random
import logging
from tornado.web import asynchronous, HTTPError
import obelisk
from obelisk import bitcoin

def random_id_number():
    return random.randint(0, 2**32 - 1)

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

class BlockHeaderHandler(BaseHTTPHandler):
    @asynchronous
    def get(self, blk_hash=None):
        if blk_hash is None:
           response = self.error_response("no block hash")
           self.send_response(response)

        try:
            blk_hash = blk_hash.decode("hex")
        except ValueError:
            response = self.error_response("Invalid block")
            self.send_response(response)

        self.application.client.fetch_block_header(blk_hash, self._callback_response)


    def _callback_response(self, ec, header_bin):
        header = obelisk.serialize.deser_block_header(header_bin)
        data = {  
                 'header_block': {
                    'version': header.version,
                    'previous_block_hash': header.previous_block_hash.encode("hex"),
                    'merkle': header.merkle.encode("hex"),
                    'timestamp': header.timestamp,
                    'bits': header.bits,
                    'nonce':header.nonce,
                } 
        }
        response_dict = self.success_response(data)
        self.send_response(response_dict)

class BlockTransactionsHandler(tornado.web.RequestHandler):
    @asynchronous
    def get(self, blk_hash=None):
        if blk_hash is None:
           response = self.error_response("no block hash")
           self.send_response(response)

        try:
            blk_hash = blk_hash.decode("hex")
        except ValueError:
            response = self.error_response("Invalid block")
            self.send_response(response)

        self.application.client.fetch_block_transaction_hashes(blk_hash, self._callback_response)

    def _callback_response(self, hash_list):
        print hash_list
        self.send_response("")

class TransactionHandler(BaseHTTPHandler):
    @asynchronous
    def get(self, tx_hash=None):
        if tx_hash is None:
            response  = self.fail_response("missing tx_hash")
            self.send_response(response)
        try:
            tx_hash = tx_hash.decode("hex")
        except ValueError:
            response = self.fail_response("invalid tx_hash")
            self.send_response(response)
        logging.info("transaction %s", tx_hash)
        self.application.client.fetch_transaction( tx_hash, self._callback_response)

    def _callback_response(self, ec, tx):
        transaction =  tx.encode("hex")
        tx_ = obelisk.bitcoin.Transaction(transaction)
        data = {
            'transaction':{
                'hash': transaction,
                'deserialize': tx_.deserialize(),
                }
        }
        response = self.success_response(data)
        self.send_response(response)

class AddressHistoryHandler(BaseHTTPHandler):
    @asynchronous
    def get(self, address=None):
        if address is None:
            raise HTTPError(400, reason="No address")

        self.address = address
        self.application.client.fetch_history(address, self._callback_response)

    def _callback_response(self,ec,history):
        address = {}
        total_balance = 0
        total_balance += sum(row[3] for row in history
                                                 if row[-1] != obelisk.MAX_UINT32)
        transactions = []
        for row in history:
            o_hash, o_index, o_height, value, s_hash, s_index, s_height = row
            def check_none( hash_):
                if hash_ is None:
                    return  None
                else:
                    return hash_.encode("hex")

            transaction = {
                    'output_hash': check_none(o_hash),'output_index': o_index,'output_height':o_height,
                    'value': value,
                    'spend_hash':check_none(s_hash), 'spend_index': s_index, 'spend_height': s_height,
                }
            transactions.append(transaction)

        address.update({'total_balance': total_balance, 
                'address':self.address, 'transactions': transactions})
        data = {'address': address}
        if not ec:
            response = self.success_response(data)
        else:
            response = self.error_response(history)
        self.send_response(response)

class HeightHandler(BlockHeaderHandler, BaseHTTPHandler):
    @asynchronous
    def get(self):
        self.application.client.fetch_last_height(self._before_callback_response)

    def _before_callback_response(self, ec, height):
        self.height = height
        self.application.client.fetch_block_header(height, self._callback_response)

    def _callback_response(self, ec, header_bin):
        header = obelisk.serialize.deser_block_header(header_bin)
        pbh = header.previous_block_hash.encode("hex")
        data = { 'last_height': self.height, 
                 'last_header_block': {
                    'hash': obelisk.serialize.hash_block_header(header).encode("hex"),
                    'version': header.version,
                    'previous_block_hash': pbh.decode("hex")[::-1].encode("hex"),
                    'merkle': header.merkle.encode("hex"),
                    'timestamp': header.timestamp,
                    'bits': header.bits,
                    'nonce':header.nonce,
                } 
        }
        response_dict = self.success_response(data)
        self.send_response(response_dict)
