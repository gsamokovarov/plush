from __future__ import absolute_import

from tornado.web import Application

from .conf import SettingDescriptor, SettingsView


class Configuration(SettingsView):
    'Upper cased settings view for the standard `tornado` settings.'

    debug = SettingDescriptor('DEBUG')

    template_path = SettingDescriptor('TEMPLATE_PATH', 'templates')
    template_loader = SettingDescriptor('TEMPLATE_LOADER')

    autoescape = SettingDescriptor('AUTOESCAPE')

    login_url = SettingDescriptor('LOGIN_URL')

    gzip = SettingDescriptor('GZIP')

    static_path = SettingDescriptor('STATIC_PATH', 'static')
    static_url_prefix = SettingDescriptor('STATIC_URL_PREFIX', '/static/')
    static_handler_class = SettingDescriptor('STATIC_HANDLER_CLASS')
    static_handler_args = SettingDescriptor('STATIC_HANDLER_ARGS')

    ui_modules = SettingDescriptor('UI_MODULES', 'modules')
    ui_methods = SettingDescriptor('UI_METHODS')

    log_function = SettingDescriptor('LOG_FUNCTION')

    cookie_secret = SettingDescriptor('COOKIE_SECRET')
    xsrf_cookies = SettingDescriptor('XSRF_COOKIES')


class Backend(Application):
    'Extended tornado application to support our custom routings.'

    def __init__(self, handlers=None, default_host='', transforms=None,
                 wsgi=False, settings=None, plush=None, **rest):

        Application.__init__(self, handlers or rest.pop('routes', None),
                                   default_host, transforms, wsgi, **rest)

        self.plush = plush

        self.settings = Configuration(self.settings)
        self.settings.update(settings or {})
