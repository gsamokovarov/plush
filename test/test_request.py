import pickle

from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase

from plush.request import Request
from plush.util.lang import tap


class TestRequestFromFunction(AsyncHTTPTestCase):
    def get_app(self):
        handler = Request.from_function(lambda req: req.finish('OK'),
                                        methods=['GET'])

        return Application([('/', handler)])

    def test_that_it_creates_requests_from_functions(self):
        def index(request): request.finish('index')
        
        index_handler = Request.from_function(index, methods=['GET'])

        self.assertTrue(issubclass(index_handler, Request))
        self.assertTrue(index_handler.get.im_func == index)

    def test_that_it_creates_request_from_functions_and_with_decorators(self):
        def once(fn): return tap(fn, lambda fn: setattr(fn, 'once', True))
        def twice(fn): return tap(fn, lambda fn: setattr(fn, 'twice', True))

        def decoo(request): request.finish('index')

        decoo_handler = Request.from_function(decoo, methods=['GET'],
                                              decorators=[once, twice])

        self.assertTrue(decoo_handler.get.im_func.once)
        self.assertTrue(decoo_handler.get.im_func.twice)

    def test_that_it_creates_request_from_functions_and_mixes_mixins(self):
        class NamedMixin(object):
            name = classmethod(lambda cls: cls.__name__)

        def mixed(request): request.finish('mixing')

        mixed_handler = Request.from_function(mixed, methods=['GET'],
                                              mixins=[NamedMixin]) 

        self.assertTrue(mixed_handler.name() == 'mixed')


class TestRequestParam(AsyncHTTPTestCase):
    def get_app(self):
        def int_parser(request):
            request.finish(str(isinstance(request.param('int', type=int), int)))
        handler = Request.from_function(int_parser, methods=['GET'])

        return Application([('/', handler)])

    def test_should_get_the_argument_as_the_given_type(self):
        response = self.fetch('/?int=24')

        self.assertEquals('True', response.body)

    def test_should_raise_http_error_on_wrong_type(self):
        response = self.fetch('/?int=abc')

        self.assertRegexpMatches(response.body, r'.*Bad Request.*')


class TestRequestAttributeRouting(AsyncHTTPTestCase):
    def get_app(self):
        def redirecter(request):
            attr = request.param('attr')

            try:
                request.finish(pickle.dumps(getattr(request, attr)))
            except AttributeError, e:
                request.finish(pickle.dumps(e))
        handler = Request.from_function(redirecter, methods=['GET'])

        return Application([('/', handler)])

    def test_should_redirect_request_calls(self):
        attr = pickle.loads(self.fetch('/?attr=%s' % 'request_method').body)

        self.assertEquals("GET", attr)

    def test_should_redirect_application_calls(self):
        attr = pickle.loads(self.fetch('/?attr=%s' % 'application_settings').body)

        self.assertEquals(self.get_app().settings, attr)

    def test_should_still_raise_attribute_errors(self):
        with self.assertRaises(AttributeError):
            error = pickle.loads(
                self.fetch('/?attr=%s' % 'application_MISSING').body)

            raise error
