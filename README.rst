============
tornadoist
============

**tornadoist** -currently- provides Mixins to execute code outside
``tornado.ioloop.IOLoop`` to avoid blocking.

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

