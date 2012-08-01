import functools

from tornado.web import asynchronous, addslash, removeslash, authenticated

from .response import Error

def before(method):
    '''
    Decorates a function to be called before the decorated `method`.

    The function itself should accept a `self` argument, as it would be called
    with the exact signature as the method.
    '''

    def decorator(filter):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            filter(self, *args, **kwargs)
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


def after(method):
    '''
    Decorates a function to be called after the decorated `method`.

    The function itself should accept a `self` argument, as it would be called
    with the exact signature as the method.

    The `filter` function will be called only if the decorated ones do not
    raise exceptions or does not explicitly return a value.
    '''

    def decorator(filter):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            if result is None:
                return filter(self, *args, **kwargs)
            return result
        return wrapper
    return decorator
