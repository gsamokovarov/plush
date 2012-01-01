import json

from plush.backend import Backend
from plush.testing import TestCase
from plush.request import Request
from plush.util.lang import tap


class TestRequestFromFunction(TestCase):
    def get_app(self):
        handler = Request.from_function(lambda req: req.finish('OK'),
                                        methods=['GET'])

        return Backend([('/', handler)])

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


class TestRequestParam(TestCase):
    def get_app(self):
        def int_parser(request):
            request.finish(str(isinstance(request.param('int', type=int), int)))

        handler = Request.from_function(int_parser, methods=['GET'])

        return Backend([('/', handler)])

    def test_should_get_the_argument_as_the_given_type(self):
        response = self.fetch('/?int=24')

        self.assertEquals('True', response.body)

    def test_should_raise_http_error_on_wrong_type(self):
        response = self.fetch('/?int=abc')

        self.assertRegexpMatches(response.body, r'.*Bad Request.*')


class TestRequestJson(TestCase):
    def get_app(self):
        def jsonable(request):
            keywords = request.param('keywords', default=False)
            tuples = request.param('tuples', default=False)
            lists = request.param('lists', default=False)
            
            if keywords:
                request.json(message='keywords', keywords=keywords)
            elif lists:
                request.json(['lists', lists])
            elif tuples:
                request.json(('tuples', tuples))
            else:
                request.json({'dictionaries': True})

        handler = Request.from_function(jsonable, methods=['GET'])

        return Backend([('/', handler)])

    def test_that_it_returns_json_from_keywords(self):
        response = self.get('/?keywords=1')

        self.assertTrue('application/json' in response.headers['Content-Type'])
        self.assertEqual(dict(message='keywords', keywords='1'),
                         json.loads(response.body))

    def test_that_it_returns_json_from_tuples(self):
        response = self.get('/?tuples=1')

        self.assertTrue('application/json' in response.headers['Content-Type'])
        self.assertEqual(['tuples', '1'], json.loads(response.body))

    def test_that_it_returns_json_from_lists(self):
        response = self.get('/?lists=1')

        self.assertTrue('application/json' in response.headers['Content-Type'])
        self.assertEqual(['lists', '1'], json.loads(response.body))

    def test_that_it_returns_json_from_dictionaries(self):
        response = self.get('/')

        self.assertTrue('application/json' in response.headers['Content-Type'])
        self.assertEqual(dict(dictionaries=True), json.loads(response.body))


class TestRequestError(TestCase):
    def get_app(self):
        def splode(request):
            exception = request.param('exception', default=False)
            status_code = request.param('status_code', default=False)
            
            if exception:
                return request.error(Exception(exception))

            if status_code:
                return request.error('Status code', int(status_code))

            class Response:
                status_code = 400
                
                def __str__(self):
                    return 'Response with %s' % self.status_code

            return request.error(Response())

        handler = Request.from_function(splode, methods=['GET'])

        return Backend([('/', handler)])

    def test_that_it_should_set_the_status_code(self):
        response = self.get('/')

        self.assertEqual(response.code, 400)
        self.assertEqual(response.body, 'Response with 400')

    def test_that_it_should_display_the_message_of_the_exception(self):
        response = self.get('/?exception=boom')

        self.assertEqual(response.code, 500)
        self.assertEqual(response.body, 'boom')

    def test_that_it_should_set_the_status_code_if_given(self):
        response = self.get('/?status_code=501')

        self.assertEqual(response.code, 501)
        self.assertEqual(response.body, 'Status code')
