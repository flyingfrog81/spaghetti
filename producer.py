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
Module used as a standalone application for testing the spaghetti server with
different data sets produced runtime.
"""

import numpy
import numpy.random
import scipy.signal
import zmqnumpy
import logging
logger = logging.getLogger(__name__)
import time

@zmqnumpy.numpy_array_sender("random", "tcp://127.0.0.1:8766")
def r_data(_max, _size, _type):
    return numpy.random.uniform(0, _max, _size).astype(_type)

@zmqnumpy.numpy_array_sender("gauss", "tcp://127.0.0.1:8766")
def g_data(_mean, _stdev, _size, _type):
    return numpy.random.normal(_mean, _stdev, _size).astype(_type)

@zmqnumpy.numpy_array_sender("window", "tcp://127.0.0.1:8766")
def w_data(_stdev, _size, _type):
    return scipy.signal.gaussian(_size, _stdev).astype(_type)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _size = 1024
    try:
        while 1:
            r_data(150, _size, numpy.float32)
            g_data(100, 10, _size, numpy.float32)
            w_data(numpy.random.randint(1, _size), _size, numpy.float32)
            time.sleep(2.0)
    except Exception, e:
        logger.error(e)
        logger.info("closing")

