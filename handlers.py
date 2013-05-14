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
from dataroom import DataRoomException

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

class CloseRoomHandler(SecuredHandler, tornado.auth.GoogleMixin):
    @tornado.web.addslash
    @tornado.web.authenticated
    def get(self, roomname):
        try:
            self.application.hotel.remove_room(roomname, self.current_user['email'])
            self.write(get_answer_dict())
        except DataRoomException, dre:
            self.write(get_answer_dict(False, dre))

class InfoHandler(tornado.web.RequestHandler):
    @tornado.web.addslash
    def get(self, name=None, format=None):
        if name == "rooms":
            logger.debug("fetching general info")
            if format == "json":
                self.write(dict(rooms=self.application.hotel.room_names()))
            else:
                self.render("generic_client.html", rooms = self.application.hotel.room_names())
        else:
            try:
                logger.debug("fetching info for room: " + name)
                config = self.application.hotel.get_room_configuration(name)
                self.write(config)
            except Exception, exc:
                self.write(get_answer_dict(False, exc))

class WSDataHandler(tornado.websocket.WebSocketHandler):
    def open(self, name, width=None):
        logger.debug("opening websocket to: " + name)
        self.name = name
        if width:
            self.width = int(width)
        else:
            self.width = None
        #save the creation time for time-based expiring
        self.date_of_birth = datetime.datetime.now()
        try:
            #add the listener to the named room
            self.room.add_client(self)
        except KeyError:
            self.close()

    def on_close(self):
        logger.debug("closing websocket to: " + self.name)
        room = self.application.hotel.get_room(self.name)
        room.remove_client(self)

    def on_message(self, msg):
        if len(msg) > 256:
            logger.warn("Message length is > 256 characters ... flooding?")
        else:
            try:
                _d = tornado.escape.json_decode(msg)
                if self.current_user['email'] == self.room.owner:
                    self.room.safe_update_config(_d)
            except:
                logger.warn("Cannot interpret message: ", msg)

    @property
    def room(self):
        return self.application.hotel.get_room(self.name)

    def __repr__(self):
        res = ""
        res += "DataStreamHandler: "
        res += self.name + "->"
        res += self.request.remote_ip
        res += " Created on: "
        res += self.date_of_birth.strftime("%d/%m/%Y %H:%M")
        return res
