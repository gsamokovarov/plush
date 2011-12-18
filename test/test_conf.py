import unittest

from plush.conf import Settings, Setting, SettingsView


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


class TestSetting(SettingBase):
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


class TestSettings(unittest.TestCase):
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


class TestSettingsView(unittest.TestCase):
    def setUp(self):
        class Configuration(SettingsView):
            static_path = Setting('STATIC_PATH', '/static/')
            static_handler_class = Setting('STATIC_HANDLER_CLASS')
            log_function = Setting('LOG_FUNCTION')

        self.Configuration = Configuration

    def test_that_it_respects_defaults(self):
        conf = self.Configuration({})

        self.assertTrue(conf['static_path'] == '/static/')

    def test_that_it_respects_configuration(self):
        conf = self.Configuration(dict(STATIC_PATH='/'))

        self.assertTrue(conf['static_path'] == '/')

    def test_that_it_can_get_with_defaults(self):
        conf = self.Configuration({})

        self.assertTrue(conf.get('static_handler_class', 'Charlie'), 'Charlie')

    def test_that_it_preserves_contains_behaviour(self):
        conf = self.Configuration({})

        self.assertFalse('log_function' in conf)

    def test_that_we_forward_getitem_only_for_defined_settings(self):
        conf = self.Configuration({})

        for key in ('static_handler_class', 'log_function'):
            self.assertFalse(key in conf)

    def test_that_when_splatted_the_dict_contains_non_sentinel_valies(self):
        conf = dict(**self.Configuration({}))

        self.assertTrue('static_path' in conf)
        self.assertFalse('log_function' in conf)
