# -*- coding: utf-8 -*-

# Copyright (c) 2012 Eren Güven
#
# Licensed under the Apache License, Version 2.0 (the "License")
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""CeleryMixin to be used with Tornado RequestHandlers"""

import functools
import logging
import os
import socket
from uuid import uuid4

import tornado.ioloop
from celery import task

__author__ = """Eren Güven <erenguven0@gmail.com>"""

@task
def celery_notifier(sockname):
    """Celery Task to notify task caller via UnixSocket and registered
    handler on IOLoop
    """
    assert sockname, 'need sockname=path/to/unixsocket kwarg'
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(sockname)
    sock.close()

class CeleryMixin(object):
    """Mixin class to run asynchronous Celery tasks with callbacks.

        class CeleryHandler(tornado.web.RequestHandler, CeleryMixin):
            @tornado.web.asynchronous
            def get(self):
                self.add_task(some_task, callback=self._on_result)

            def _on_result(self, result):
                do_something_with_result(result)
                self.finish()

    Using `tornado.gen`

        class CeleryHandler(tornado.web.RequestHandler, CeleryMixin):
            @tornado.web.asynchronous
            @tornado.gen.engine
            def get(self):
                Task = tornado.gen.Task
                result = yield Task(self.add_task, some_task, 'argx')
                self.write('Hello %s World!' % result)
                self.finish()

    """

    def add_task(self, taskname, *args, **kwargs):
        """Run a Celery task. All args and kwargs except `callback` are
        passed to task.

        :param taskname: celery task
        :keyword callback: callable with a single argument (task result)

        This method creates a random UnixSocket under /tmp/ for
        communication, registers a handler on `tornado.ioloop.IOLoop`
        with its fd, calls `taskname.apply_async(args, kwargs)` and
        links to notifier subtask to be run upon successful completion.

        :attr:`celery_result` contains return value of apply_async
        """
        user_cb = kwargs.pop('callback')
        assert callable(user_cb)

        ioloop = tornado.ioloop.IOLoop().instance()
        fname = '/tmp/task_socket_%s' % uuid4()
        # create & bind socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(fname)
        sock.listen(1)
        # pass down input callback
        callback = functools.partial(self._on_complete, user_cb)
        ioloop.add_handler(sock.fileno(), callback, ioloop.READ)
        # subtask
        link = celery_notifier.subtask(args=(fname,), immutable=True)
        self.celery_result = taskname.apply_async(args, kwargs, link=link)
        self.celery_socket = sock

    def _on_complete(self, callback, *args):
        """Callback-In-The-Middle to do some cleanup before calling the
        actual callback.
        """
        logging.debug('FD Events: %s', str(args))
        # task completed, remove handler & socket
        ioloop = tornado.ioloop.IOLoop().instance()
        ioloop.remove_handler(self.celery_socket.fileno())
        fname = self.celery_socket.getsockname()
        self.celery_socket.close()
        os.remove(fname)
        # sanity check
        assert self.celery_result.ready()
        # run callback
        callback(self.celery_result.result)
