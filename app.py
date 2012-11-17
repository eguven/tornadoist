# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Copyright (c) 2012 Eren Güven
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Demo app with CeleryMixin"""

import logging
import os.path

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from celery import Celery

from tcelerymixin import CeleryMixin

# MongoDB Broker & Backend
celery = Celery('app', broker='mongodb://', backend='mongodb://')

@celery.task
def echo(i):
    return i

class CeleryHandler(tornado.web.RequestHandler, CeleryMixin):
    @tornado.web.asynchronous
    def get(self):
        self.add_task(echo, 'Vegetable', callback=self._on_result)

    def _on_result(self, result):
        self.write('Hello %s World!' % result)
        self.finish()

    # or simply using tornago.gen.engine
#    @tornado.web.asynchronous
#    @tornado.gen.engine
#    def get(self):
#        result = yield tornado.gen.Task(self.add_task, echo, 'Vegetable2')
#        self.write('Hello %s World!' % result)
#        self.finish()

app_handlers = [
                (r"/", CeleryHandler),
    ]

settings = dict(
    debug = True,
    )

# define port for command-line
define("host", default="127.0.0.1")
define("port", default=8888, type=int)

app = tornado.web.Application(app_handlers,**settings)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    options.logging = "debug"
    tornado.options.parse_command_line()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port, address=options.host)

    tornado.ioloop.IOLoop.instance().start()
