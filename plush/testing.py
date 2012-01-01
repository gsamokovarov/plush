from tornado.escape import url_escape
from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncHTTPTestCase

__all__ = 'TestCase test_case_for'.split()


class PostRequest(HTTPRequest):
    '''
    HTTP request which accepts a dictionary as its body and converts it to the
    apropriate HTTP query.
    '''

    def __init__(self, url, body, **kwargs):
        kwargs['body'] = '&'.join('%s=%s' % (url_escape(k), url_escape(v))
                                  for (k, v) in body.iteritems())

        super(self.__class__, self).__init__(url, method='POST', **kwargs)


class TestCase(AsyncHTTPTestCase):
    'Basic asynchronous test case supporting easier post client requests.'

    def post(self, path, body, **kwargs):
        self.http_client.fetch(PostRequest(self.get_url(path), body, **kwargs),
                               self.stop)
        return self.wait()

    get = AsyncHTTPTestCase.fetch


#: Make `nose` or any other test name guessing library happy.
def case_for(app):
    'Creates a test case class for the given `app`lication.`'

    class AppSpecificTestCase(TestCase):
        def get_app(self):
            return app.prepare()

    return AppSpecificTestCase


test_case_for = case_for
