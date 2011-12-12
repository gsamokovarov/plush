from __future__ import absolute_import

import os

try:
    from importlib import import_module
except ImportError:
    from .util.compat.importlib import import_module

from .util.lang import try_in_order, identity, Sentinel

__all__ = "SettingDescriptor Settings SettingsView".split()

try:
    import yaml
except:
    YAML_ENABLED = False
else:
    YAML_ENABLED = True


class SettingDescriptor(object):
    '''
    Descriptor allowing to redirect instance attributes to the settings object.

    While the settings object itself does not allow explicit type conversion
    during the settings extraction, the descriptor does.

    Supports defaults which are returned when the setting name is not found in
    the settings object.
    '''

    DEFAULT_SETTINGS_ATTR = 'settings'
    DEFAULT_TYPE = staticmethod(identity)

    def __init__(self, name, type=None, default=None, settings_attr=None):
        self.name = name
        self.default = default
        self.type = type or self.DEFAULT_TYPE
        self.settings_attr = settings_attr or self.DEFAULT_SETTINGS_ATTR

    def __get__(self, instance, owner):
        settings = getattr(instance or owner, self.settings_attr)

        return self.type(settings.get(self.name, self.default))

    def __set__(self, obj, value):
        settings = getattr(obj, self.settings_attr)
        settings[self.name] = self.type(value)


class Settings(dict):
    '''
    The settings container object.

    Supports `dot notation`, meaning that you can get elements like attributes
    and creation from a YAML markup.
    '''

    if YAML_ENABLED:
        def from_yaml(cls, markup, filename=True):
            '''
            Creates a :class:`Settings` object from YAML `markup` or YAML file
            name if `filename` is truthful.
            '''

            if filename:
                with open(markup) as yaml_file:
                    return cls(yaml.load(yaml_file))

            return cls(yaml.load(markup))
    else:
        def from_yaml(cls, markup, filename=True):
            raise NotImplementedError("You need pyyaml for this.")

    from_yaml = classmethod(from_yaml)

    @classmethod
    def from_env(cls, envar):
        '''
        Creates a :class:`Settings` object from the environment variable
        `envar` pointing to a Python file, Python module or YAML file.
        '''

        if envar not in os.environ:
            raise ValueError("Expected %s in environment" % envar)

        return try_in_order(cls.from_pyfile, cls.from_yaml, cls.from_module,
                            args=(os.environ[envar],))

    @classmethod
    def from_pyfile(cls, filename):
        'Creates a :class:`Settings` object from a python file.'

        namespace = {}
        execfile(filename, namespace)

        return cls(namespace)

    @classmethod
    def from_object(cls, obj):
        'Creates a :class:`Settings` object from a regular python object.'

        return cls(obj.__dict__)

    @classmethod
    def from_module(cls, modulename):
        '''
        Creates a :class:`Settings` object from a module.

        The module must be importable from the current execution point.
        '''

        return cls.from_object(import_module(modulename))

    def has(self, *options):
        'Checks whether the settings include all of the specified options.'

        return all(opt in self for opt in options)

    def has_some_of(self, *options):
        'Checks whether the settings include any of the specified options.'

        return any(opt in self for opt in options)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError, exc:
            raise AttributeError(exc)


class SettingsView(dict):
    '''
    Settings view represents a collection of setting descriptors, linked to a
    settings container.

    The setting descriptors can be accessed using the `__getitem__` notation
    because we forward the descriptors. Further more we redirect item inclusion
    to the underlying settings so we get correct behaviour for the current
    `tornado` application use cases.
    '''

    def __init__(self, settings):
        dict.__init__(self)
        self.update(type(self).__dict__)

        self.settings = settings

    def get(self, setting, default=None):
        value = getattr(self, setting, Sentinel)

        return default if value is Sentinel else value

    def __contains__(self, setting):
        return setting in self.settings

    def __getitem__(self, setting):
        try:
            return getattr(self, setting)
        except AttributeError:
            raise KeyError(setting)
