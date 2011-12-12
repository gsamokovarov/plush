from time import time as now

from tornado import stack_context
from tornado.ioloop import IOLoop


class Deferred(object):
    'Deferred execution object.'

    io_loop_class = IOLoop

    def __init__(self, deadline, callback, io_loop=None):
        self.io_loop = io_loop or self.io_loop_class.instance()
        self.timeout = self.io_loop.add_timeout(now() + deadline,
                                                stack_context.wrap(callback))

    def cancel(self):
        'Cancels the current deferred object.'

        return self.io_loop.remove_timeout(self.timeout)
