from rest_handlers import BaseHTTPHandler
from tornado.web import asynchronous, HTTPError

def get_urls(uri_space):
    uri = uri_space + "hello/"
    return  [
       uri + "addresses/([^/]*)(?:/)?", FriendlyAddress
    ]


class FriendlyAddress(BaseHTTPHandler):
    @asynchronous
    def get(self,address):
        pass
