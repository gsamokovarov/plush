import unittest

from plush.conf import Settings, Setting


class SettingBase(unittest.TestCase):
    def setUp(self):
        self.Holder = type('Holder', (object,), {
            'settings': Settings({
                'int': 2,
                'bool': True,
                'falsy': ''
            }),

            'int': Setting('int'),
            'bool': Setting('bool'),
            'falsy': Setting('falsy'),
        })

        self.TypedHolder = type('TypedHolder', (self.Holder,), {
            'int': Setting('int', type=int),
            'bool': Setting('bool', type=bool),
            'falsy': Setting('falsy', type=bool),
        })


class SettingTest(SettingBase):
    def test_that_it_bounds_properly_to_instances(self):
        Holder = self.Holder()

        self.assertEqual(Holder.int, 2)
        self.assertEqual(Holder.bool, True)
        self.assertEqual(Holder.falsy, '')

    def test_that_it_converts_values_properly(self):
        holder = self.TypedHolder()

        self.assertEqual(holder.int, 2)
        self.assertEqual(holder.bool, True)
        self.assertEqual(holder.falsy, False)


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.Plain = type('Plain', (object,), {})

    def test_that_it_has_attribute_access(self):
        settings = Settings({'foo': 'bar'})

        self.assertEqual(settings.foo, settings['foo'])

    def test_that_it_loads_from_objects(self):
        obj = self.Plain()
        obj.bacon = 'Fresh'

        settings = Settings().from_object(obj)

        self.assertTrue('bacon' in settings)
        self.assertEqual(settings.bacon, 'Fresh')
