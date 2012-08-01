class classonlymethod(classmethod):
    '''
    Descriptor for making class only methods.

    A `classonly` method is a class method, which can be called only from the
    class itself and not from instances. If called from an instance will
    raise ``AttributeError``.
    '''

    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError(
                "Class only methods can not be called from an instance")

        return classmethod.__get__(self, instance, owner)


class cachedproperty(object):
    '''
    Property that memoize it's target method return value.
    '''

    # The implementation is ripped off django.

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        result = instance.__dict__[self.getter.__name__] = self.getter(instance)

        return result


def curry(function, *curried_args, **curried_kw):
    '''
    Curries a function or a method with a positional or keyworded arguments.

    To be used in places where `functools.partial` can not. For example to
    curry methods while still in the class definition. This will not work with
    `functools.partial` as it returns a `Partial` object, instead of raw
    function.
    '''

    def curried_function(*args, **kw):
        return function(*(curried_args + args), **dict(curried_kw, **kw))
    
    return curried_function


def tap(object, interceptor):
    '''
    Calls interceptor with `obj` and then return `object`.
    '''

    interceptor(object)

    return object


def setdefaultattr(object, attr, default=None):
    '''
    Sets a `default` `attr`ibute value on a `object`.

    Behaves like :meth:`dict.setdefault`, setting the attribute default value
    only if the attribute does not exists on the `obj`ect.
    '''

    if hasattr(object, attr):
        return attr

    return tap(default, lambda default: setattr(object, attr, default))


def try_in_order(*functions, **kw):
    '''
    Tries to execute the `functions` in order and returns the first one that
    succeedes.

    `args` and `kwargs` if passed as keyword arguments are delegated down to
    the functions.
    '''

    if not functions:
        raise TypeError("You must give at least one function to try.")

    for fn in functions:
        try:
            return fn(*kw.get('args', []), **kw.get('kwargs', {}))
        except:
            continue

    raise


class SentinelType(object):
    def __nonzero__(self):
        return False
    __bool__ = __nonzero__

#: Unique singleton.
Sentinel = SentinelType()

#: Returns itself.
identity = lambda obj: obj
