#!/usr/bin/env python
#coding=utf-8

from distutils.core import setup

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
      scripts = ["scripts/spaghetti"],
      requires = ["tornado", "pyzmq", "numpy", "zmqnumpy"],
     )
