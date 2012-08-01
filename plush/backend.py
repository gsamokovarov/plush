from __future__ import absolute_import

from tornado.web import Application, URLSpec

from .conf import Setting, SettingsView


class Configuration(SettingsView):
    '''
    Upper cased settings view for the standard `tornado` settings.
    '''

    debug = Setting('DEBUG')

    template_path = Setting('TEMPLATE_PATH', 'templates')
    template_loader = Setting('TEMPLATE_LOADER')

    autoescape = Setting('AUTOESCAPE')

    login_url = Setting('LOGIN_URL')

    gzip = Setting('GZIP')

    static_path = Setting('STATIC_PATH', 'static')
    static_url_prefix = Setting('STATIC_URL_PREFIX')
    static_handler_class = Setting('STATIC_HANDLER_CLASS')
    static_handler_args = Setting('STATIC_HANDLER_ARGS')

    ui_modules = Setting('UI_MODULES')
    ui_methods = Setting('UI_METHODS')

    log_function = Setting('LOG_FUNCTION')

    cookie_secret = Setting('COOKIE_SECRET')
    xsrf_cookies = Setting('XSRF_COOKIES')


class Backend(Application):
    '''
    Extended tornado application to support our custom routings.
    '''

    def __init__(self, handlers=None, default_host='', transforms=None,
                 wsgi=False, settings=None, plush=None, **rest):

        settings = Configuration(settings or {})
        settings.update(rest)

        self.plush = plush

        Application.__init__(self, rest.pop('routes', None) or handlers,
                                   default_host, transforms, wsgi, **settings)
