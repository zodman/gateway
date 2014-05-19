#!/usr/bin/env python

import tornado.options
import tornado.web
import tornado.websocket
import obelisk
import threading
import code

import config

# Install Tornado reactor loop into Twister
# http://www.tornadoweb.org/en/stable/twisted.html
from tornado.platform.twisted import TwistedIOLoop
from twisted.internet import reactor
TwistedIOLoop().install()
from crypto2crypto import CryptoTransportLayer

from tornado.options import define, options, parse_command_line

parse_command_line()


import rest_handlers
import obelisk_handler
import querysocket_handler
import jsonchan
import broadcast
import ticker

define("port", default=8888, help="run on the given port", type=int)

global ioloop
ioloop = tornado.ioloop.IOLoop.instance()

class GatewayApplication(tornado.web.Application):

    def __init__(self, service):

        settings = dict(debug=True)
        settings.update(options.as_dict())
        client = obelisk.ObeliskOfLightClient(service)
        self.client = client
        self.obelisk_handler = obelisk_handler.ObeliskHandler(client)
        self.brc_handler = broadcast.BroadcastHandler()
        self.p2p = CryptoTransportLayer(config.get('p2p-port', 8889), config.get('external-ip', '127.0.0.1'))
        self.p2p.join_network(config.get('seeds', []))
        self.json_chan_handler = jsonchan.JsonChanHandler(self.p2p)
        self.ticker_handler = ticker.TickerHandler()
        #websocket uri space
        handlers = [
            ## WebSocket Handler
            (r"/", querysocket_handler.QuerySocketHandler)
        ]

        # helloobelisk uri space
        uri_space= r"/rest/v1/"
        other_handlers = [
            (uri_space + r'net(?:/)?', rest_handlers.NetHandler),
            (uri_space + r'height(?:/)?', rest_handlers.HeightHandler),
            (uri_space + r'address/([^/]*)(?:/)?', rest_handlers.AddressHistoryHandler),
            (uri_space + r'tx/([^/]*)(?:/)?', rest_handlers.TransactionHandler),
            (uri_space + r'block/([^/]*)(?:/)?', rest_handlers.BlockHeaderHandler),
            (uri_space + r"block/([^/]*)/transactions(?:/)?",  rest_handlers.BlockTransactionsHandler),
        ]
        all_handlers = other_handlers + handlers
        tornado.web.Application.__init__(self, all_handlers, **settings)


class DebugConsole(threading.Thread):

    daemon = True

    def __init__(self, application):
        self.application = application
        super(DebugConsole, self).__init__()
        self.start()

    def run(self):
        console = code.InteractiveConsole()
        code.interact(local=dict(globals(), **locals()))

def main(service):
    application = GatewayApplication(service)
    tornado.autoreload.start(ioloop)
    application.listen(config.get('websocket-port', 8888))
    #debug_console = DebugConsole(application)
    reactor.run()

if __name__ == "__main__":
    service = config.get("obelisk-url", "tcp://127.0.0.1:9091")
    try:
        main(service)
    except KeyboardInterrupt:
        reactor.stop()

