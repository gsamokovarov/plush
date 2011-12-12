from __future__ import absolute_import

import re
import json

from tornado.web import RequestHandler, HTTPError
from tornado.escape import to_unicode, json_encode as to_json

from .util.lang import identity, cachedproperty, tap
from .util.http import parse_content_type, encode_content_type

__all__ = "Request HTTPError".split()


def redirect_from(*targets):
    'Redirects `target` attribute `dot` calls to underscore methods.'

    target_pattern = '|'.join(targets)

    class Redirection(object):
        ATTR_REDIRECT_RE = \
            re.compile(r'(?P<target>%s)_(?P<attr>\w+)' % target_pattern)

        def __getattr__(self, attr):
            match = self.ATTR_REDIRECT_RE.match(attr)

            if match is not None:
                target = getattr(self, match.group('target'))
                redirected_attr = getattr(target, match.group('attr'))

                return redirected_attr

            return object.__getattr__(self, attr)

    return Redirection


class Request(RequestHandler, redirect_from('request', 'application')):
    'Custom tornado `RequestHandler` providing nicer API.'

    @classmethod
    def from_function(cls, func, methods, decorators=None, mixins=None):
        '''
        Creates a new `Request` from a function, to serve as a specific HTTP
        verbs dispatcher.

        The function must accept at least one positional argument, as it would
        be bound directly to the created class. You can think of it as `self`
        of an instance method of the current class.

        If `decorators` is given it should be a list of decorators to be
        applied in order to the `func`.

        If `mixins` is given it should be a list of mixins to be inherited by
        the newly created class. They will be inherited in that order.
        '''

        if any(method not in cls.SUPPORTED_METHODS for method in methods):
            raise ValueError('methods %r must be one of %r' %
                             (methods, cls.SUPPORTED_METHODS))

        for decorator in decorators or []:
            func = decorator(func)

        parents = tuple([cls] + [mixin for mixin in mixins or []])

        base = type(func.__name__, parents, {})
        for method in methods:
            setattr(base, method.lower(), func)

        return base

    @property
    def method(self):
        'Returns the request method.'

        return self.request_method

    @property
    def headers(self):
        'Returns the request headers.'

        return self.request_headers

    @property
    def data(self):
        'Returns the raw request data.'

        return self.request_data

    @cachedproperty
    def mime(self):
        'Returns the request mime type object.'

        return Mimetype(self)

    @property
    def content_type(self):
        'Returns the request content type'

        return self.mime.type

    @cachedproperty
    def cookie(self):
        'Returns the request cookie object.'

        return Cookie(self)

    @cachedproperty
    def like(self):
        '''
        Returns the possible request data converters.

        The only supported conversion right now is the `json` one.
        '''

        return Converters(self)

    def param(self, name, default=RequestHandler._ARG_DEFAULT,
                    strip=True, type=identity):
        '''
        Returns the value of the argument with the given name, converting it to
        type if specified.

        The contact for `type` is that it have to take one argument and raise
        `ValueError` on bad input.
        '''

        try:
            return type(RequestHandler.get_argument(self, name, default, strip))
        except ValueError, message:
            raise HTTPError(400, str(message))

    def error(self, error=None, status_code=500):
        '''
        Sends an `error` to the client.

        If the `error` is an object with `status_code` attribute, it would be
        used as a status code. Otherwise you can specify your own code with the
        `code` argument. This works well for :class:`HTTPError` subclasses.

        If the `error` is not an exception, it can be string and you can
        specify a custom code.

        Optionally the `error` object can be missed altogether and you can send
        just and status code. This is useful if you want to set a JSON error
        with :meth:`jsonify` and set a custom status code.

        This method finishes the request.

        Returns the error message as a string.
        '''

        self.set_status(getattr(error, 'status_code', status_code))

        return tap(str(error or ''), lambda obj: self.try_finish(obj))

    def json(self, obj=None, **json):
        '''
        Sends a JSON out of an `obj`ect or keyword parameters.

        To create a JSON out of keywords you must not specify an object, you
        should just use keywords. The `obj`ect has higher presedense and the
        keywords will be ignored.

        Returns the created JSON.
        '''

        if obj is not None:
            return tap(to_json(obj), lambda json: self.write(json))
        
        return tap(to_json(json), lambda json: self.write(json))

    def send(self, obj):
        '''
        Sends a object to the output buffer.

        If the object is `list`, `tuple` or `dict` it will be send it as a JSON
        and we will set the content type to _application/json_.

        If the object is an exception it will finalize the request, set the
        status code to 500 if the `obj`ect does not have `status_code`
        attribute or the value that if the `status_code` is present.

        Otherwise will write a unicode representation of the object.
        '''

        if isinstance(obj, (dict, list, tuple)):
            return self.json(obj)
        elif isinstance(obj, Exception):
            return self.error(obj)

        return tap(to_unicode(obj), lambda obj: self.write(obj))

    def try_finish(self, chunk):
        if self._auto_finish:
            return self.write(chunk)

        self.finish(chunk)


class RequestComposition(object):
    def __init__(self, request):
        self.request = request


class Converters(RequestComposition):
    '''
    The methods below convert the raw request data to other formats, if
    possible.
    '''

    @cachedproperty
    def json(self):
        '''
        Returns the parsed json body, if the request is a JSON, e.g. has a
        content type of `application/json`.

        Otherwise `None` is returned.
        '''

        if self.request.content_type == 'application/json':
            return json.loads(self.request.data)


class Cookie(RequestComposition):
    '''
    Composition around a :class:`Request` instance to provide nicer API for
    cookie getting and setting.
    '''

    def get(self, name, default=None):
        return self.request.get_cookie(name, default)

    def set(self, *args, **kwargs):
        self.request.set_cookie(*args, **kwargs)


class Mimetype(RequestComposition):
    '''
    Composition around a :class:`Request` instance to provide nicer API for
    mime types setting and getting.
    '''

    def __init__(self, request):
        RequestComposition.__init__(self, request)

        raw_content_type = self.request.headers.get('Content-Type')
        self.type, self.params = parse_content_type(raw_content_type)

    def get(self, default=None):
        'Returns the content type or `default` if not specified.'

        return self.type or default

    def set(self, type, **params):
        'Sets a `type` for the current request.'

        self.request.set_headers('Content-Type',
                                 encode_content_type(type, params))

    def param(self, name, default=None):
        'Gets a parameter by `name` or returns `default`.'

        return self.params.get(name, default)
