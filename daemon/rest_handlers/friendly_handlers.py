from rest_handlers import BaseHTTPHandler
from tornado.web import asynchronous, HTTPError
import obelisk
from obelisk import bitcoin
O_HASH = 0
O_INDEX = 1
O_HEIGHT = 2
VALUE = 3
S_HASH = 4
S_INDEX = 5
S_HEIGHT = 6

def get_urls(uri_space):
    uri = uri_space + "f/"
    return  [
       (uri + r"address/([^/]*)(?:/)?", FriendlyAddress),
    ]


class FriendlyAddress(BaseHTTPHandler):
    @asynchronous
    def get(self,address):
        self.address = address
        self.application.client.fetch_history(self.address, self._callback_response)

    def _callback_response(self,error_code,history):
        if error_code:
            response = self.error_response("error fetch")
            return self.send_response(response)
        address = {}
        total_balance,in_value, out_value = 0,0,0
        out_unconfirmed, out_confirmed = 0,0
        in_unconfirmed, in_confirmed = 0,0
        for row in history:
            if row[S_HASH]:
                if not row[S_HEIGHT]:
                    out_unconfirmed += row[VALUE]
                else:
                    out_confirmed += row[VALUE]
            if row[O_HEIGHT]:
                in_confirmed += row[VALUE]
            else:
                in_unconfirmed += row[VALUE]

        address.update({
                'balance': {
                    'confirmed':in_confirmed-out_confirmed, 
                    'unconfirmed': in_unconfirmed-out_unconfirmed,
                    },
                'in':{'confirmed':in_confirmed, 'unconfirmed': in_unconfirmed},
                'out':{'confirmed':out_confirmed, 'unconfirmed':out_unconfirmed},
                'tx_count':len(history),
                'address':self.address,
                })
        data = {'address': address}
        self.send_response(data)
