from __future__ import absolute_import

import os

try:
    from importlib import import_module
except ImportError:
    from .util.compat.importlib import import_module

from .util.lang import try_in_order, tap, identity, Sentinel

__all__ = "Setting Settings SettingsView".split()

try:
    import yaml
except ImportError:
    YAML_ENABLED = False
else:
    YAML_ENABLED = True


class Setting(object):
    '''
    Descriptor allowing to redirect instance attributes to the settings object.

    While the settings object itself does not allow explicit type conversion
    during the settings extraction, the descriptor does.

    Supports defaults which are returned when the setting name is not found in
    the settings object.
    '''

    DEFAULT_SETTINGS_ATTR = 'settings'
    DEFAULT_TYPE = staticmethod(identity)

    def __init__(self, name, default=None, type=None, settings_attr=None):
        self.name = name
        self.default = default or Sentinel
        self.type = type or self.DEFAULT_TYPE
        self.settings_attr = settings_attr or self.DEFAULT_SETTINGS_ATTR

    def __get__(self, instance, owner):
        settings = getattr(instance, self.settings_attr)

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
        def from_yaml(self, markup, filename=True):
            '''
            Creates a :class:`Settings` object from YAML `markup` or YAML file
            name if `filename` is truthful.
            '''

            if not filename:
                return tap(self, lambda self: self.update(yaml.load(markup)))

            with open(markup) as file:
                return tap(self, lambda self: self.update(yaml.load(file)))
    else:
        def from_yaml(self, markup, filename=True):
            raise NotImplementedError("You need pyyaml for this.")

    def from_env(self, envar):
        '''
        Creates a :class:`Settings` object from the environment variable
        `envar` pointing to a Python file, Python module or YAML file.
        '''

        if envar not in os.environ:
            raise ValueError("Expected %s in environment" % envar)

        return try_in_order(self.from_pyfile, self.from_yaml, self.from_module,
                            args=(os.environ[envar],))

    def from_pyfile(self, filename):
        '''
        Creates a :class:`Settings` object from a python file.
        '''

        namespace = {}
        execfile(filename, namespace)

        return tap(self, lambda self: self.update(namespace))

    def from_object(self, obj):
        '''
        Creates a :class:`Settings` object from a regular python object.
        '''

        return tap(self, lambda self: self.update(obj.__dict__))

    def from_module(self, modulename, package=None):
        '''
        Creates a :class:`Settings` object from a module.

        The module must be importable from the current execution point. If you
        specify an absolute import, you must give the `package` to be imported
        from.
        '''

        return self.from_object(import_module(modulename, package))

    def has(self, *options):
        '''
        Checks whether the settings include all of the specified options.
        '''

        return all(opt in self for opt in options)

    def has_some_of(self, *options):
        '''
        Checks whether the settings include any of the specified options.
        '''

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
    because we forward the descriptors.
    '''

    def __init__(self, settings):
        dict.__init__(self)

        self.settings = settings

        class_attrs, dict_attrs = dir(type(self)), dir(dict)
        possibilities = set(class_attrs).difference(dict_attrs)

        for name in possibilities:
            setting = getattr(self, name)
            if setting is not Sentinel:
                self[name] = setting
