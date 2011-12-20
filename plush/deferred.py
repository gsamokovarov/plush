from datetime import timedelta as delta

from tornado import stack_context
from tornado.ioloop import IOLoop


class Deferred(object):
    '''
    Deferred execution object.

    It executes a `callback` at a given `deadline` of milliseconds.
    Can be canceled, if not already executed, with :meth:`cancel`.
    '''

    io_loop_class = IOLoop

    def __init__(self, deadline, callback, io_loop=None):
        self.io_loop = io_loop or self.io_loop_class.instance()
        self.timeout = self.io_loop.add_timeout(delta(milliseconds=deadline),
                                                stack_context.wrap(callback))

    def cancel(self):
        'Cancels the current deferred object.'

        return self.io_loop.remove_timeout(self.timeout)

    def cancel_if(self, condition):
        'Cancel the current deffered object if the `condition` is true.'

        if condition:
            return self.cancel()
