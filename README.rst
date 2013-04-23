============
tornadoist
============

**tornadoist** -currently- provides Mixins to execute code outside
``tornado.ioloop.IOLoop`` to avoid blocking. These are:

- CeleryMixin: Celery Tasks
- ProcessMixin: Functions in separate process

Both support results, avoids polling or timeouts. More info below.

Demo app included. (Celery with ``mongodb://`` preconfigured in demo app)

CeleryMixin
-----------

**CeleryMixin** is a Mixin class to use with ``tornado.web.RequestHandler``
that provides a Tornado-like interface to running Celery tasks on TornadoServer.

HowTO
`````

Using ``tornado.gen`` ::

    from tornado import web, gen
    from tornadoist import CeleryMixin

    class CeleryHandler(tornado.web.RequestHandler, CeleryMixin):
        @web.asynchronous
        @gen.engine
        def get(self):
            result = yield gen.Task(self.add_task, some_task, 'somearg')
            self.write('Hello %s World!' % result)
            self.finish()

Or using explicit callback ::

    class CeleryHandler(tornado.web.RequestHandler, CeleryMixin):
        @tornado.web.asynchronous
        def get(self):
            self.add_task(some_task, callback=self._on_result)

        def _on_result(self, result):
            do_something_with_result(result)
            self.finish()

ProcessMixin
------------

**ProcessMixin** is a Mixin class to use with ``tornado.web.RequestHandler``
that provides a Tornado-like interface to running functions with
``multiprocessing.Process`` outside IOLoop.

HowTO
`````

Using ``tornado.gen`` ::

    from tornado import web, gen
    from tornadoist import ProcessMixin

    class ProcessHandler(tornado.web.RequestHandler, ProcessMixin):
        @tornado.web.asynchronous
        @tornado.gen.engine
        def get(self):
            result = yield tornado.gen.Task(self.add_task, my_blocking_function,
                                            'somearg', some_kwarg=42)
            self.write('Hello Process World! %s' % result)
            self.finish()

License
^^^^^^^

`Apache License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_
