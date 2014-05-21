from rest_handlers import BaseHTTPHandler
from tornado.web import asynchronous, HTTPError
import obelisk

def get_urls(uri_space):
    uri = uri_space + "hello/"
    return  [
       uri + "addresses/([^/]*)(?:/)?", FriendlyAddress
    ]


class FriendlyAddress(BaseHTTPHandler):
    @asynchronous
    def get(self,address):
        self.address = address
        self.application.client.fetch_history(address, self._callback_response)

    def _callback_response(self,error_code,history):
        if error_code:
            response = self.error_response("error fetch")
            return self.send_response(response)
        address = {}
        total_balance = 0
        total_balance += sum(row[3] for row in history
                                                 if row[-1] != obelisk.MAX_UINT32)

        address.update({
                'balance': total_balance, 
                'confirmedBalance':"",
                'address':self.address
                })
        data = {'address': address}
        if not ec:
            response = self.success_response(data)
        else:
            response = self.error_response(history)
        self.send_response(response)
