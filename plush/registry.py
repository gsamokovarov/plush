from __future__ import absolute_import

from abc import ABCMeta
from collections import defaultdict

from .util.lang import classonlymethod

__all__ = "Registrable Registry register registry".split()


# Will I have any benefit of making this thread local?
REGISTRABLE_INFO = defaultdict(list)


class Registrable(object):
    '''
    Mixin providing a registrable support for a base class.

    Every subclass can register itself by calling the 'register' method.
    '''

    @classonlymethod
    def register(cls):
        '''
        Registers the current class to it's own base class registry.

        If the class defines a class method named ``on_registration``, it will be
        executed upon registration and it's returned value will be stored as
        data and will be returned for it by ``Registry.entries_with_data_for``.
        The returned value of ``on_registration`` must be ``None`` or a mapping.
        '''

        if isinstance(cls, Registry):
            raise TypeError('Can not register a registry.')

        for base in cls.__bases__:
            if issubclass(base, Registry):
                if hasattr(cls, 'on_registration'):
                    data = cls.on_registration()

                    if data is None:
                        data = {}
                else:
                    data = {}

                REGISTRABLE_INFO[base].append((cls, data))

                break
        else:
            raise TypeError('No registry ancsestor found!')

    @classonlymethod
    def make_registry(cls):
        '''
        Makes the current class a registry.
        '''

        #for base in inspect.getmro(cls):
        #    if issubclass(base, Registry):
        #        raise TypeError(
        #            'Can not make multiple registries in one chain.')

        REGISTRABLE_INFO[cls] # It's a side effect of the default dict.


class Registry(object):
    '''
    Psuedo class used for registry subclass checking.

    A registry is every class including the ``Registrable`` mixin and being
    called the ``make_registry`` class method.
    '''

    __metaclass__ = ABCMeta

    @classmethod
    def __subclasshook__(cls, other_class):
        if cls is Registry:
            return other_class in REGISTRABLE_INFO

        return NotImplemented

    @staticmethod
    def entries_with_data_for(cls):
        '''
        Returns the entries with their bounded data for the specified registry.

        Raises an ``TypeError`` when the specified class is not a registry.
        '''

        if not issubclass(cls, Registry):
            raise TypeError('Not a registry!')

        return REGISTRABLE_INFO[cls]

    @staticmethod
    def entries_for(cls):
        '''
        Returns the entries for the specified registry.

        Raises an ``TypeError`` when the specified class is not a registry.
        '''

        if not issubclass(cls, Registry):
            raise TypeError('Not a registry!')

        return [r for (r, _) in Registry.entries_with_data_for(cls)]

    @staticmethod
    def clear(cls=None):
        '''
        Clears the specified registry of its entries or all of purges all for
        the registries with their entries of no class is specified.
        '''

        if cls is not None:
            if issubclass(cls, Registry):
                REGISTRABLE_INFO[cls] = []
            else:
                raise TypeError('Not a registry!')
        else:
            REGISTRABLE_INFO.clear()


#: More pythonic, non classy interface.
entries_for = Registry.entries_for
entries_with_data_for = Registry.entries_with_data_for


def registry(cls):
    '''
    Class decorator for making registries.

    Provides different syntax for making registries than 
    ``Base.make_registry()``.
    '''
    
    try:
        cls.make_registry()
    except AttributeError:
        raise TypeError('The class must inherit Registrable')
    else:
        return cls


def register(cls):
    '''
    Class decorator for class registration.

    Provides different syntax for registering to registries than
    ``Sub.register()``.
    '''

    try:
        cls.register()
    except AttributeError:
        raise TypeError('The class must inherit Registrable')
    else:
        return cls
