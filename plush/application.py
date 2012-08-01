from __future__ import absolute_import

from collections import OrderedDict

from tornado.ioloop import IOLoop

from .deferred import Deferred
from .request import Request
from .backend import Backend
from .server import Server
from .conf import Settings
from .util.lang import tap, curry

__all__ = "Plush".split()


class Plush(object):
    '''
    The :class:`Plush` abstracts a whole web application.
    '''

    #: The default request class.
    request_class = Request

    #: The default application backend.
    backend_class = Backend

    #: The default server class.
    server_class = Server

    #: The default deffered class.
    deferred_class = Deferred

    #: The default io loop class.
    io_loop_class = IOLoop

    def __init__(self, module_name, io_loop=None, **user_settings):
        self.module_name = module_name
        self.io_loop = io_loop or self.io_loop_class.instance()
        self.settings = Settings(user_settings)
        self.routes = OrderedDict()
        self.transforms = []
        self.decorators = []
        self.mixins = []

    #: Features and customizations.

    def transform(self, transform):
        '''
        Use a output `transform` for the application.
        '''

        return tap(self, lambda self: self.transforms.append(transform))

    def decorator(self, decorator):
        '''
        Use a `decorator` for the requests.
        '''

        return tap(self, lambda self: self.decorators.append(decorator))

    def mixin(self, mixin):
        '''
        Use a `mixin` for the reguests.
        '''

        return tap(self, lambda self: self.mixins.append(mixin))

    def use(self, feature, obj):
        '''
        Use a `obj`ect for a `feature`.

        The currently supported features are:
          * `transform` - use an `object` for a transform.
          * `decorator` - use a `decorator` for every request function.
          * `mixin` - use a mixin for every request handler.

        For every feature, there is a method named the same way. If that method
        suites your context or preferences better, you can use it instead.
        '''

        if feature == 'transform':
            return self.transform(obj)
        elif feature == 'decorator':
            return self.decorator(obj)
        elif feature == 'mixin':
            return self.mixin(obj)
        else:
            raise ValueError('Unsupported feature %s. Supported ones are %r.' %
                             (feature, ['transform', 'decorator', 'mixin']))

    #: Routing with and without HTTP verbs.

    def route(self, pattern, methods, **options):
        '''
        Routes a function accepting HTTP `pattern` and HTTP `methods`.
        '''

        def wrapper(func):
            self.routes[pattern] = func

            func.pattern = pattern
            func.methods = methods
            func.decorators = options.get('decorators', []) + self.decorators
            func.mixins = options.get('mixins', []) + self.mixins

            return func

        return wrapper

    get = curry(route, methods=['GET'])
    head = curry(route, methods=['HEAD'])
    post = curry(route, methods=['POST'])
    delete = curry(route, methods=['DELETE'])
    put = curry(route, methods=['PUT'])
    options = curry(route, methods=['OPTIONS'])

    #: Async utilities.

    def defer(self, milliseconds, callback):
        '''
        Defers the execution of a `callback` for `milliseconds`.
        '''

        return self.deferred_class(milliseconds, callback, self.io_loop)

    delay = defer

    #: Filters.

    def filter(self, *functions, **options):
        '''
        Creates a filter for the specified functions.

        There is a required keyword parameter of `type` which determinates what
        the type of the filter will be.

        Types:
          * before - runs the filter before the handler code
          * after  - runs the filter after the handler code, if it did not
                     raised an exception or explicitly returned a value.

        You will rarely have to use it explicitly, use :meth:`before` and
        :meth:`after` instead.
        '''

        from .decorators import before, after

        def wrapper(filter):
            def decorate_safetly(func, action, filter):
                func.decorators.append(lambda f: action(func)(filter))

            for func in functions:
                if not hasattr(func, 'pattern') or func.pattern not in self.routes:
                    raise ValueError('Function %s is not routed' % func.__name__)

                action = before if options['type'] == 'before' else after
                decorate_safetly(func, action, filter)

            return filter

        return wrapper

    before = curry(filter, type='before')
    after = curry(filter, type='after')

    #: Application running.

    def prepare(self):
        '''
        Creates request handlers out of the currently routed functions and
        creates a backend tornado application to run with them.
        '''

        routes = []

        for pattern, func in self.routes.iteritems():
            kw = dict(decorators=func.decorators, mixins=func.mixins)
            methods = dict((method, func) for method in func.methods)
            request = self.request_class.from_function(func, methods, **kw)

            routes.append((pattern, request))

        return self.backend_class(routes, settings=self.settings,
                                  transforms=self.transforms, plush=self)

    def run(self, **options):
        server = self.server_class(self.prepare(), self.io_loop)
        server.serve(**options)
