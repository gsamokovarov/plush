import unittest

from plush.registry import Registrable, Registry, \
                           register, registry


class RegistrableTest(unittest.TestCase):
    def tearDown(self):
        Registry.clear()

    def test_that_it_registers_properly(self):
        Ent = type('Ent', (Registrable,), {})
        Ent.make_registry()

        self.assertTrue(issubclass(Ent, Registry))

        Sub = type('Sub', (Ent,), {})
        Sub.register()

        self.assertTrue(Sub in Registry.entries_for(Ent))

    def test_registry_unregisterable(self):
        with self.assertRaises(TypeError):
            Ent = type('Ent', (Registrable,), {})
            Ent.make_registry()

            # We should blow up here.
            Ent.register()

    def test_specific_registry_clearing(self):
        Ent = type('Ent', (Registrable,), {})
        Ent.make_registry()

        Sub = type('Sub', (Ent,), {})
        Sub.register()

        self.assertTrue(Sub in Registry.entries_for(Ent))

        Registry.clear(Ent)

        self.assertFalse(Sub in Registry.entries_for(Ent))

    def test_global_registries_clearing(self):
        Ent1 = type('Ent1', (Registrable,), {})
        Ent1.make_registry()

        Ent2 = type('Ent2', (Registrable,), {})
        Ent2.make_registry()

        Registry.clear()

        with self.assertRaises(TypeError):
            Registry.entries_for(Ent1)

        with self.assertRaises(TypeError):
            Registry.entries_for(Ent2)

    def test_on_registration_data_binding(self):
        Ent = type('Ent', (Registrable,), {
            'on_registration': classmethod(lambda cls: {
                    'non_entry_specific': True
            })
        })
        Ent.make_registry()

        Sub = type('Sub', (Ent,), {})
        Sub.register()

        self.assertEqual(
            [(Sub, {'non_entry_specific': True})],
            Registry.entries_with_data_for(Ent)
        )

    def test_decorators(self):
        @registry
        class Ent(Registrable): pass

        self.assertTrue(issubclass(Ent, Registry))

        @register
        class Sub(Ent): pass

        self.assertTrue(Sub in Registry.entries_for(Ent))
        
    def test_decorator_on_non_registrable(self):
        with self.assertRaises(TypeError):
            @registry
            class Ent(object): pass

        with self.assertRaises(TypeError):
            @register
            class Sub(object): pass

    #def test_multiple_registries_along_the_chain(self):
    #    Ent = type('Ent1', (Registrable,), {})
    #    Ent.make_registry()

    #    with self.assertRaises(TypeError):
    #        SpecEnt = type('SpecEnt', (Ent,), {})
    #        SpecEnt.make_registry()

