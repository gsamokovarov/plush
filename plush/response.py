import httplib

from tornado.web import HTTPError

__all__ = 'Error response_for'.split()


class Error(HTTPError):
    '''
    The base class for HTTP errors.

    Not intended to be send to the client, but if you do so, it will send an
    error with status code of 500.
    '''

    status_code = 500

    def __init__(self, log_message, *args):
        self.log_message = str(log_message)
        self.args = args


def response_for(status_code, name):
    '''
    Creates a response class for `status_code` with `name`.

    If the status code is above 400 the response class will be a subclass of
    :class:`Error`.
    '''

    name = ''.join(name.replace('-', ' ').split())
    base = Error if status_code >= 400 else object

    return type(name, (base,), dict(status_code=status_code))


for status_code, response_name in httplib.responses.iteritems():
    response = response_for(status_code, response_name)

    globals().setdefault(response.__name__, response)

del status_code, response_name, response
