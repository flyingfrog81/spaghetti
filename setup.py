#!/usr/bin/env python
#coding=utf-8

from distutils.core import setup
import os

CONFDIR = "/etc/spaghetti/"

# Install configuration directory in /etc/spaghetti or in 
# ~/.spaghetti for copying or updating default 
# configuration files
#
# Where do i have to put this code for custom installation???!!

try:
    os.makedirs(CONFDIR)
except OSError, _oe:
    if _oe.errno == 13: #Permission denied
        print "Cannot create directory in /etc, permission denied"
        CONFDIR = os.path.expanduser("~/.spaghetti/")
        try:
            print "using directory %s" % (CONFDIR,)
            os.makedirs(CONFDIR)
        except OSError, __oe:
            if __oe.errno == 17: #directory exists
                pass
            else:
                raise
    elif _oe.errno == 17: #directory /etcspaghetti/ already exists
        pass
    else:
        raise

setup(
      name = "spaghetti",
      version = "0.2.0",
      description = "Publish binary array data via WebSocket",
      author = "Marco Bartolini",
      author_email = "marco.bartolini@gmail.com",
      maintainer = "Marco Bartolini",
      license = "mit",
      url = "https://bitbucket.org/flyingfrog/spaghetti",
      packages = ["spaghetti"],
      package_dir = {"spaghetti" : "src"},
      package_data = {"spaghetti" : ["static/js/*.js",
                                     "static/js/flot/*.js",
                                     "templates/*.html"]},
      data_files = [(CONFDIR, ['config/spaghetti.conf'])],
      scripts = ["scripts/spaghetti"],
      requires = ["tornado", "pyzmq", "numpy", "zmqnumpy"],
     )

