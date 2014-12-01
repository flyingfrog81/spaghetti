#coding=utf-8

# Copyright (c) 2013 Marco Bartolini, marco.bartolini@gmail.com
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

# Standard library imports
import os
import logging
logger = logging.getLogger(__name__)

# Third party imports
import tornado.web
import zmq

# Project imports
import datachannel
import handlers

VERSION = "simple"
MAIN_CONF = "/etc/spaghetti/spaghetti.conf"
USER_CONF = "~/.spaghetti/spaghetti.conf"

class SpaghettiApplication(tornado.web.Application):
    def __init__(self, **kwargs):
        self.channel_collection = datachannel.ChannelCollection()
        self.http_host = None
        self.http_port = None
        self.ws_base_url = "/ws/"
        _handlers = [
                (r"/list/?(json)?/?", handlers.ListHandler, 
                                 dict(view="list.html")),
                (r"/detail/(\w+)/?(vizname)?/?", handlers.DetailHandler,
                                dict(view="detail.html")),
                (r"/close/(\w+)/?", handlers.CloseChannelHandler),
                (r"%s(\w+)/?" % (self.ws_base_url,), handlers.WSDataHandler),
                ]
        settings = dict(
                debug = True,
                template_path = os.path.join(os.path.dirname(__file__), "templates"),
                static_path = os.path.join(os.path.dirname(__file__), "static"),
                )
        settings.update(kwargs)
        tornado.web.Application.__init__(self, _handlers, **settings)

    def update_channel(self, data):
        logger.debug("application update via zmqnumpy data")
        self.channel_collection.update_channel(data)

    def close_channel(self, name):
        self.channel_collection.remove_channel(name)

    def get_channel(self, name):
        return self.channel_collection.get_channel(name)

def cmd_line():
    """
    Entry point for \'spaghetti\' command line script.
    """
    from tornado.options import define, options
    from zmq.eventloop import ioloop, zmqstream
    import os
    ioloop.install()

    # define spaghetti options
    define("zmq_socks", 
           default = "tcp://127.0.0.1:8766", 
           multiple = True,
           help = "Comma separated list of zmq sockets")
    define("http_host", 
           default = "127.0.0.1")
    define("http_port",
           default = 8765)
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    define("template_path",
           default = template_path)
    static_path = os.path.join(os.path.dirname(__file__), "static")
    define("static_path",
           default = static_path)
    define("debug",
           default = False)

    # parse options from config files and command line
    if os.path.exists(MAIN_CONF):
        tornado.options.parse_config_file(MAIN_CONF, final=False)
    if os.path.exists(os.path.expanduser(USER_CONF)):
        tornado.options.parse_config_file(os.path.expanduser(USER_CONF), final=False)
    tornado.options.parse_command_line()
    if not isinstance(options.zmq_socks, list):
        zsocks = [options.zmq_socks]
    else:
        zsocks = options.zmq_socks
    if options.debug:
        logger.info("running in debug mode")
    logger.debug("Template path: %s" % (options.template_path,))
    logger.debug("Static path: %s" % (options.static_path,))

    # Create the app
    app = SpaghettiApplication(debug = options.debug,
                               static_path = options.static_path,
                               template_path = options.template_path)
    # HTTP stuff
    app.listen(options.http_port, address=options.http_host)
    app.http_host = options.http_host
    app.http_port = options.http_port

    # ZMQ stuff
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    for _zsock in zsocks:
        logger.info("binding %s" % (_zsock,))
        socket.bind(_zsock)
    zstream = zmqstream.ZMQStream(socket)
    zstream.on_recv(app.update_channel)

    # start the event loop
    logger.info("starting io loop")
    logger.info("http host: " + str(options.http_host))
    logger.info("http port: " + str(options.http_port))
    ioloop.IOLoop.instance().start()
