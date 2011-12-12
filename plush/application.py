from __future__ import absolute_import

from tornado.ioloop import IOLoop

from .deferred import Deferred
from .request import Request
from .backend import Backend
from .server import Server
from .conf import Settings
from .util.lang import cachedproperty, tap


class Plush(object):
    'The :class:`Plush` abstracts a whole web application.'

    DEFAULT_SETTINGS_ENV = 'PLUSH_SETTINGS_MODULE'

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

    def __init__(self, module_name, settings_env=None, settings_file=None, 
                       io_loop=None, complain_about_settings=False,
                       **user_settings):

        self.module_name = module_name

        self.io_loop = io_loop or self.io_loop_class.instance()

        self.user_settings = Settings(user_settings)
        self.settings_env = settings_env or self.DEFAULT_SETTINGS_ENV
        self.settings_file = settings_file

        self.complain_about_settings = complain_about_settings

        self.transforms = []
        self.decorators = []
        self.mixins = []

        self.routes = []

    @cachedproperty
    def settings(self):
        '''
        Returns the appication settings.

        There are two types of settings - _global_ and _user_ settings. The
        user settings are the one set in the :class:`Plush` constructor, the
        one loaded from a file, are global. The user settings are applied on
        top of the global ones, so they can override them.
        '''

        try:
            if self.settings_file:
                settings = Settings.from_pyfile(self.settings_file)
            else:
                settings = Settings.from_env(self.settings_env)
        except:
            if self.complain_about_settings:
                raise

            settings = Settings()
        else:
            settings.update(self.user_settings)

        return settings

    #: Features and customizations.

    def transform(self, transform):
        'Use a output `transform` for the application.'

        return tap(self, lambda self: self.transforms.append(transform))

    def decorator(self, decorator):
        'Use a `decorator` for the requests.'

    def mixin(self, mixin):
        'Use a `mixin` for the reguests'

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

    def route(self, path, methods, **kw):
        'Routes a function accepting HTTP `path` and HTTP `methods`.'

        def decorator(fn):
            request = self.request_class.from_function(fn, methods, **kw)
            self.routes.append((path, request))

            return fn

        return decorator

    def get(self, path, **kw):
        return self.route(path, methods=['GET'], **kw)

    def head(self, path, **kw):
        return self.route(path, methods=['HEAD'], **kw)

    def post(self, path, **kw):
        return self.route(path, methods=['POST'], **kw)

    def delete(self, path, **kw):
        return self.route(path, methods=['DELETE'], **kw)

    def put(self, path, **kw):
        return self.route(path, methods=['PUT'], **kw)

    def options(self, path, **kw):
        return self.route(path, methods=['OPTIONS'], **kw)

    #: Async utilities.

    def defer(self, milliseconds, callback):
        'Defers the execution of a `callback` for `milliseconds`.'

        return self.deferred_class(milliseconds, callback, self.io_loop)

    def run(self, **options):
        backend = self.backend_class(self.routes, settings=self.settings,
                                     transforms=self.transforms, plush=self)
        server = self.server_class(backend, self.io_loop)
        server.serve(**options)
