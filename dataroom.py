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

import datetime
import logging
logger = logging.getLogger(__name__)

"""
Room attributes 
"""
CONFIG_ATTRIBUTES = ['name', 'binary', 'shape', 'size', 'dtype', 'url']

class DataRoomException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

def dataroom_error(message):
    """
    Log the message and raise a DataRoomException with the same message
    """
    logger.exception(message)
    raise DataRoomException(message)

class DataRoom(object):
    """
    A DataRoom manages a set of data and clients.
    Clients enter the data room and subscribe to the set of data, whenever data
    is updated the room notifies all the clients connected and sends them the 
    newly updated data.
    """
    def __init__(self, name, owner, data=None, binary=False):
        self.clients = set()
        bd = datetime.datetime.now()
        self.configuration = dict(name=name, 
                binary=binary,
                date_of_birth = bd,
                last_connection = bd,
                last_data_update = bd,
                open = True,
                empty_since = None,
                clients = 0,
                )
        self.data = data
        self.owner = owner

    @property
    def name(self):
        return self.configuration['name']

    def close(self):
        """
        Disconnects all the clients and closes the room
        """
        logger.debug("closing room: " + self.name)
        for client in self.clients:
            client.close()
        self.configuration['open'] = False

    def add_client(self, client):
        """
        Add a client to the room if the room is open. 
        Sends the actual data to the client just connected and subscribes
        it to all successive data updates.
        """
        if not self.configuration['open']:
            logger.debug("trying to access a closed DataRoom: " + self.name) 
            return
        logger.debug("add a client to the room: " + self.name)
        self.clients.add(client)
        self.configuration['last_connection'] = datetime.datetime.now()
        self.configuration['empty_since'] = None
        if self.data:
            client.write_message(self.data, self.configuration['binary'])
        self.configuration['clients'] += 1

    def remove_client(self, client):
        """
        Remove the client from the DataRoom. 
        If no more clients are present sets the DataRoom empty status.
        """
        logger.debug("remove client from room: " + self.name)
        self.clients.remove(client)
        if not self.clients:
            self.configuration['empty_since'] = datetime.datetime.now()
        self.configuration['clients'] -= 1

    def update_data(self, data):
        """
        Update data inside the DataRoom and sets the last update time.
        This method does not implement any transmission logics.
        """
        self.data = data
        self.configuration['last_data_update'] = datetime.datetime.now()

    def broadcast_data(self):
        """
        Broadcast actual data of the DataRoom to all connected clients.
        """
        for client in self.clients:
            client.write_message(self.data, self.configuration['binary'])

    def safe_update_config(self, _dict):
        try:
            for k in CONFIG_ATTRIBUTES:
                _dict.pop(k)
        except KeyError:
            pass
        self.configuration.update(_dict)

class DataHotel(object):
    """
    A collection of DataRoom objects.
    This class is essentially a singleton and is instantiated once per 
    application wrapping some logics around the DataRoom collection. 
    It's here just for convenience and code readability.
    """
    def __init__(self):
        self.rooms = {}

    def add_room(self, name, owner=None, data=None):
        """
        @raise DataRoomException if trying to use a room name that already
        exists
        """
        if self.rooms.has_key(name):
            dataroom_error("room already exists: " + name)
            #logger.debug("room already exists: " + name)
            #raise DataRoomException("room already exists: " + name)
        self.rooms[name] = DataRoom(name, owner, data, True)
        logger.debug("added room: " + name)

    def room_names(self):
        return self.rooms.keys()

    def get_room(self, name):
        try:
            room = self.rooms[name]
            return room
        except KeyError:
            dataroom_error("room does not exist: " + name)

    def get_room_configuration(self, name):
        room = self.get_room(name)
        return room.configuration

    def remove_room(self, name, owner):
        """
        Close and remove a named room from the hotel.
        @raise DataRoomException if named room is not present
        """
        try:
            if not self.rooms[name].owner == owner:
                dataroom_error("Unauthorized user for room: " + name)
            self.rooms[name].close()
            self.rooms.pop(name)
            logger.debug("removed room: " + name)
        except KeyError:
            dataroom_error("remove room does not exist: " + name)

    def update_room(self, message):
        """
        Update one of the rooms according to message data. 
        The name of the room and every necessary information must be contained
        in the message tuple. Message is intended to be composed as defined by zmqnumpy module
        protocol for the interchange of numpy arrays.
        """
        _uuid = message[0] #now it is not used but it's in the message body
        name = message[1]
        #logger.debug("update message: " + str(message))
        try:
            room = self.rooms[name]
            room.update_data(message[-1])
            room.broadcast_data()
        except KeyError:
            dataroom_error("update room does not exist: " + name)

