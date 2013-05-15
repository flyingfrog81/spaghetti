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

"""
Classes:
    - DataChannel
    - ChannelCollection
    - DataChannelException
"""

import datetime
import logging
logger = logging.getLogger(__name__)

class DataChannelException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

def datachannel_error(message):
    """
    Log the message and raise a DataChannelException with the same message
    """
    logger.exception(message)
    raise DataChannelException(message)

class DataChannel(object):
    """
    A DataChannel manages a set of data and clients.
    Clients enter the data channel and subscribe to the set of data, whenever data
    is updated the channel notifies all the clients connected and sends them the 
    newly updated data.
    """
    def __init__(self, name, owner, data=None, binary=False):
        self.clients = set()
        bd = datetime.datetime.now()
        self.name = name 
        self.binary = binary #Contains binary data
        self.creation_datetime = bd
        self.last_connection = None #Last client connection
        self.is_open = True
        self.is_empty = True #True if no clients are connected
        self.empty_since = bd
        self.data = data
        if data:
            self.last_data_update = bd
        else:
            self.lsat_data_update = None
        self.owner = owner
        #TODO: we want names to be dot compliant proj.sub1.d1 ...
        #TODO: owner will become a regular expression

    @property
    def configuration(self):
        return dict(
                    name = self.name,
                    binary = self.binary,
                    creation_datetime = self.creation_datetime,
                    last_connection = self.last_connection,
                    is_open = self.is_open,
                    is_empty = self.is_empty,
                    empty_since = self.empty_since,
                    last_data_update = self.last_data_update
                   )

    def close(self):
        """
        Disconnects all the clients and closes the channel
        """
        logger.debug("closing channel: " + self.name)
        for client in self.clients:
            client.close()
        self.is_open = False

    def add_client(self, client):
        """
        Add a client to the channel if the channel is open. 
        Sends the actual data to the client just connected and subscribes
        it to all successive data updates.
        """
        if not self.is_open:
            logger.debug("trying to access a closed DataChannel: " + self.name) 
            return
        logger.debug("add a client to the channel: " + self.name)
        self.clients.add(client)
        self.last_connection = datetime.datetime.now()
        self.empty_since = None
        if self.data:
            client.write_message(self.data, self.configuration['binary'])

    def remove_client(self, client):
        """
        Remove the client from the DataChannel. 
        If no more clients are present sets the DataChannel empty status.
        """
        logger.debug("remove client from channel: " + self.name)
        self.clients.remove(client)
        if not self.clients:
            self.is_empty = True
            self.empty_since = datetime.datetime.now()

    def update_data(self, data):
        """
        Update data inside the DataChannel and sets the last update time.
        This method does not implement any transmission logics.
        """
        self.data = data
        self.last_data_update = datetime.datetime.now()

    def broadcast_data(self):
        """
        Broadcast actual data of the DataChannel to all connected clients.
        """
        for client in self.clients:
            client.write_message(self.data, self.binary)

class ChannelCollection(object):
    """
    A collection of DataChannel objects.
    This class is essentially a singleton and is instantiated once per 
    application wrapping some logics around the DataChannel collection. 
    It's here just for convenience and code readability.
    """
    def __init__(self):
        self.channels = {}

    def __iter__(self):
        return self.channels.itervalues()

    def add_channel(self, name, owner=None, data=None):
        """
        @raise DataChannelException if trying to use a channel name that already
        exists
        """
        if self.channels.has_key(name):
            datachannel_error("channel already exists: " + name)
        self.channels[name] = DataChannel(name, owner, data, True)
        logger.debug("added channel: " + name)

    def channel_names(self):
        return self.channels.keys()

    def get_channel(self, name):
        try:
            channel = self.channels[name]
            return channel
        except KeyError:
            datachannel_error("channel does not exist: " + name)

    def get_channel_configuration(self, name):
        channel = self.get_channel(name)
        return channel.configuration

    def close_channel(self, name):
        """
        Close and remove a named channel from the Collection.
        @raise DataChannelException if named channel is not present
        """
        channel = self.get_channel(name)
        channel.close()
        self.channels.pop(name)
        logger.debug("removed channel: " + name)

    def update_channel(self, message):
        """
        Update one of the channels according to message data. 
        The name of the channel and every necessary information must be contained
        in the message tuple. Message is intended to be composed as defined by zmqnumpy module
        protocol for the interchange of numpy arrays.
        """
        owner = message[0]
        name = message[1]
        #TODO: add shape information to the channel
        if not name in self.channel_names():
            self.add_channel(name, owner, message[-1])
        else: # Channel already present
            channel = self.get_channel(name)
            if not owner == channel.owner: #TODO: this will become a match
                logger.debug("cannot update channel %s: %s is not the owner" %
                             (name, owner,))
            else:
                channel.update_data(message[-1])
                channel.broadcast_data()

