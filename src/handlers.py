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

# Standard library imports
import logging
logger = logging.getLogger(__name__)
import datetime
import functools

# Third party imports
import tornado.web
import tornado.websocket
import tornado.escape
import tornado.auth

# Project imports
import datachannel

try:
    #Here we try to patch the json_encode function in order
    #to let it convert datetime objects
    import json

    class DateTimeJSONEncoder(json.JSONEncoder):
        def default(self, o):
            try:
                return o.strftime("%d/%m/%Y %H:%M:%S")
            except:
                return json.JSONEncoder.default(self, o)

    original_doc = tornado.escape.json_encode.__doc__
    tornado.escape.json_encode = functools.partial(json.dumps, cls=DateTimeJSONEncoder)
    tornado.escape.json_encode.__doc__ = original_doc
except ImportError:
    logger.warning("cannot find json module, datetime objects won't be serialized")
    pass

def get_answer_dict(success=True, exc=None):
    if success:
        return dict(success=True)
    elif exc:
        return dict(success=False, message=exc.message)
    else:
        return dict(success=False)

class CloseChannelHandler(tornado.web.RequestHandler):
    @tornado.web.addslash
    def get(self, channel_name):
        logger.debug("CloseChannelHandler.get(%s)" % (channel_name,))
        try:
            self.application.channels.close_channel(channel_name)
            self.write(get_answer_dict())
        except datachannel.DataChannelException, dce:
            self.write(get_answer_dict(False, dce))

class ListHandler(tornado.web.RequestHandler):
    def initialize(self, view="list.html"):
        self.view = view

    @tornado.web.addslash
    def get(self, response_format="html"):
        logger.debug("ListHandler.get(response_format=%s)" % (response_format,))
        if response_format == "json":
            self.write(dict(
                        channels = [channel.configuration for channel in
                        self.application.channel_collection],
                           ) 
                      )
        else:
            self.render(self.view,
                        channels=self.application.channel_collection)

class InfoHandler(tornado.web.RequestHandler):
    def initialize(self, view="detail.html"):
        self.view = view

    @tornado.web.addslash
    def get(self, name, response_format="html"):
        logger.debug("InfoHandler.get(name=%s, response_format=%s)" % (name, response_format,))
        try:
            channel = self.application.get_channel(name)
        except Exception, exc:
            self.write(get_answer_dict(False, exc))
        if response_format == "json":
            self.write(channel.configuration)
        else:
            self.render(self.view, channel)

class WSDataHandler(tornado.websocket.WebSocketHandler):
    def open(self, name):
        logger.debug("opening websocket to: " + name)
        self.name = name
        #save the creation time for time-based expiring
        self.creation_datetime = datetime.datetime.now()
        try:
            #add the listener to the named channel
            self.channel.add_client(self)
        except KeyError:
            self.close()

    def on_close(self):
        logger.debug("closing websocket to: " + self.name)
        self.channel.remove_client(self)

    @property
    def channel(self):
        return self.application.channels.get_channel(self.name)

    def __str__(self):
        res = ""
        res += "WSDataHandler: "
        res += self.name + "->"
        res += self.request.remote_ip
        res += " Created on: "
        res += self.creation_datetime.strftime("%d/%m/%Y %H:%M")
        return res
