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


class cachedproperty(property):
    '''
    Property that memoize it's target method return value.

    Currently does not support attribute setting re-memoizing. Will support it
    if a proper use case is found.
    '''

    def __get__(self, instance, owner):
        if not hasattr(self, 'memoized'):
            self.memoized = self.fget(instance or owner)

        return self.memoized


def tap(obj, interceptor):
    'Calls interceptor with `obj` and then return `obj`.'

    interceptor(obj)
    return obj


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


#: Returns itself.
identity = lambda obj: obj

#: Unique singleton.
Sentinel = object()
