import unittest

from plush.util.http import parse_content_type, encode_content_type


class TestParseContentType(unittest.TestCase):
    def test_that_it_parses_just_content_types(self):
        self.assertEqual(parse_content_type('application/text'),
                         ('application/text', {}))

    def test_that_it_parses_content_type_and_params(self):
        self.assertEqual(parse_content_type('application/text; charset=utf-8'),
                         ('application/text', {'charset': 'utf-8'}))
            
    def test_that_it_skimms_incompete_params(self):
        self.assertEqual(parse_content_type('application/text; charset'),
                         ('application/text', {}))


class TestEncodeContentType(unittest.TestCase):
    def test_that_it_creates_proper_params(self):
        self.assertEqual(encode_content_type('application/text', {
                                                 'charset': 'utf-8'
                                             }),
                         'application/text;charset=utf-8')

    def test_that_it_encodes_without_params(self):
        self.assertEqual(encode_content_type('application/text'),
                         'application/text')
