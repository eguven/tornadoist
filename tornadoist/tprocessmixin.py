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

"""ProcessMixin to be used with Tornado RequestHandlers"""

import functools
import logging
import os
import socket
from multiprocessing import Process, Pipe
from uuid import uuid4
import time

import tornado.ioloop

__author__ = """Eren Güven <erenguven0@gmail.com>"""

def run_as_process(sockname, pipe, target=None, args=None, kwargs=None):
    """Run `target` with `args` as a :class:`~multiprocessing.Process`
    and once its done, notify ``sock`` using :meth:`~socket.socket.connect`
    so the caller knows result is available on :class:`~multiprocessing.Pipe`
    eg. run_as_process('/tmp/1337.sock', pipe_connection, target=my_func, args=(42,))
    """
    assert sockname, 'need sockname=path/to/unixsocket kwarg'
    assert callable(target), "target kwarg not callable"
    if args: assert isinstance(args, tuple), "args kwarg not a tuple or None"

    def wrapper():
        pipe.send(target(*args, **kwargs)) # send result
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) # poke
        sock.connect(sockname)
        time.sleep(5) # not sure if necessary
        sock.close()
        pipe.close()

    p = Process(target=wrapper)
    p.start()

class ProcessMixin(object):
    """Mixin class to run tasks in :class:`~multiprocessing.Process`
    asynchronously.

        class ProcessHandler(tornado.web.RequestHandler, ProcessMixin):
            @tornado.web.asynchronous
            def get(self):
                self.add_task(some_task, callback=self._on_result)

            def _on_result(self, result):
                do_something_with_result(result)
                self.finish()

    Using `tornado.gen`

        class ProcessHandler(tornado.web.RequestHandler, ProcessMixin):
            @tornado.web.asynchronous
            @tornado.gen.engine
            def get(self):
                Task = tornado.gen.Task
                result = yield Task(self.add_task, some_task, 'argx')
                self.write('Hello %s World!' % result)
                self.finish()

    """

    def add_task(self, taskname, *args, **kwargs):
        """Run a function in a Process. All args and kwargs except
        `callback` are passed to task.

        :param taskname: a `callable`
        :keyword callback: callable with a single argument (task result)

        This method creates a random UnixSocket under /tmp/ for
        communication, registers a handler on `tornado.ioloop.IOLoop`
        with its fd, creates a `Pipe` for communicating back the
        result and runs `taskname` using `run_as_process`. Which runs
        the given task, sends result back through and connects to the
        UnixSocket to let IOLoop know
        """
        user_cb = kwargs.pop('callback')
        assert callable(user_cb)

        ioloop = tornado.ioloop.IOLoop().instance()
        fname = '/tmp/proc_socket_%s' % uuid4()
        # create & bind socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(fname)
        sock.listen(1)
        # pass down input callback
        callback = functools.partial(self._on_complete, user_cb)
        ioloop.add_handler(sock.fileno(), callback, ioloop.READ)
        # subprocess
        self.tor_conn, proc_conn = Pipe()
        run_as_process(fname, proc_conn, target=taskname,
                       args=args, kwargs=kwargs)
        self.process_socket = sock

    def _on_complete(self, callback, *args):
        """Callback-In-The-Middle to do some cleanup before calling the
        actual callback.
        """
        logging.debug('FD Events: %s', str(args))
        # task completed, remove handler & socket, get result from pipe
        ioloop = tornado.ioloop.IOLoop().instance()
        ioloop.remove_handler(self.process_socket.fileno())
        fname = self.process_socket.getsockname()
        self.process_socket.close()
        os.remove(fname)
        # sanity check
        assert self.tor_conn.poll()
        # run callback
        result = self.tor_conn.recv()
        self.tor_conn.close()
        callback(result)
