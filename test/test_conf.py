import unittest

from plush.conf import Settings, SettingDescriptor


class SettingDescriptorBase(unittest.TestCase):
    def setUp(self):
        self.Holder = type('Holder', (object,), {
            'settings': Settings({
                'int': 2,
                'bool': True,
                'falsy': ''
            }),

            'int': SettingDescriptor('int'),
            'bool': SettingDescriptor('bool'),
            'falsy': SettingDescriptor('falsy'),
        })

        self.TypedHolder = type('TypedHolder', (self.Holder,), {
            'int': SettingDescriptor('int', type=int),
            'bool': SettingDescriptor('bool', type=bool),
            'falsy': SettingDescriptor('falsy', type=bool),
        })

class SettingDescriptorTest(SettingDescriptorBase):
    def test_that_it_bounds_properly_to_classes(self):
        Holder = self.Holder

        self.assertEqual(Holder.int, 2)
        self.assertEqual(Holder.bool, True)
        self.assertEqual(Holder.falsy, '')

    def test_that_it_bounds_properly_to_instances(self):
        Holder = self.Holder()

        self.assertEqual(Holder.int, 2)
        self.assertEqual(Holder.bool, True)
        self.assertEqual(Holder.falsy, '')

    def test_that_it_converts_values_properly(self):
        Holder = self.TypedHolder

        self.assertEqual(Holder.int, 2)
        self.assertEqual(Holder.bool, True)
        self.assertEqual(Holder.falsy, False)


class SettingsTest(unittest.TestCase):
    pass
