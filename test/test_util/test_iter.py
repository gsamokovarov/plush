import unittest

from plush.util.iter import apply_defaults_from


class ApplyFromDefaultsTest(unittest.TestCase):
    def test_that_it_applies_values_from_a_dict_to_another(self):
        defaults = {'foo': 'bar'}

        self.assertEqual(defaults, apply_defaults_from(defaults, to={}))

    def test_that_it_applies_values_only_if_not_present(self):
        defaults = {'foo': 'bar', 'baz': 'car'}

        self.assertEqual({'foo': 'qar', 'baz': 'car'},
                         apply_defaults_from(defaults, {'foo': 'qar'}))
