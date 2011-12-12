import httplib
import unittest

from plush import response
from plush.response import response_for, Error


class TestResponseNamespace(unittest.TestCase):
    def test_that_it_contains_everything_from_httplib_responses(self):
        assert_has = lambda attr: self.assertTrue(hasattr(response, attr))

        for status_code, name in httplib.responses.iteritems():
            assert_has(''.join(name.replace('-', ' ').split()))


class TestResponseFor(unittest.TestCase):
    def test_that_it_creates_error_for_the_appropriate_codes(self):
        self.assertTrue(issubclass(response_for(400, '_'), Error))
        self.assertFalse(issubclass(response_for(399, '_'), Error))

    def test_that_responses_have_proper_status_codes(self):
        self.assertEqual(response_for(400, '_').status_code, 400)
