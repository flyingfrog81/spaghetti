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
import dataroom
import handlers

VERSION = "simple"

class SpaghettiApplication(tornado.web.Application):
    def __init__(self, **kwargs):
        self.hotel = dataroom.DataHotel()
        _handlers = [
                (r"/close/(\w+)/?", handlers.CloseRoomHandler),
                (r"/info/(\w+)/?(json)?/?", handlers.InfoHandler),
                (r"/ws/(\w+)/?", handlers.WSDataHandler),
                ]
        settings = dict(
                debug = True,
                template_path = os.path.join(os.path.dirname(__file__), "templates"),
                static_path = os.path.join(os.path.dirname(__file__), "static"),
                cookie_secret = "cca0679f-618f-4b81-824e-0920ea0051c8",
                )
        settings.update(kwargs)
        tornado.web.Application.__init__(self, _handlers, **settings)

    def update(self, data):
        logger.debug("application update via zmq data")
        try:
            self.hotel.update_room(data)
        except:
            pass

    def close_room(self, name):
        self.hotel.remove_room(name)

if __name__ == '__main__':
    from tornado.options import define, options
    from zmq.eventloop import ioloop, zmqstream
    ioloop.install()
    define("zmq_port", default=8766)
    define("http_port", default=8765)
    tornado.options.parse_command_line()
    # HTTP stuff
    app = SpaghettiApplication()
    app.listen(options.http_port)
    # ZMQ stuff
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind("tcp://127.0.0.1:" + str(options.zmq_port))
    zstream = zmqstream.ZMQStream(socket)
    zstream.on_recv(app.update)
    # EVENT LOOP
    logger.info("starting io loop")
    logger.info("http port: " + str(options.http_port))
    logger.info("zmq port: " + str(options.zmq_port))
    ioloop.IOLoop.instance().start()
