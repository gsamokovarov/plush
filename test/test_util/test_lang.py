import time
import unittest


from plush.util.lang import classonlymethod, cachedproperty, \
                            identity, try_in_order, Sentinel


class ClassOnlyMethodTest(unittest.TestCase):
    def setUp(self):
        class Tester(object):
            @classonlymethod
            def special_method(cls):
                return cls
        
        self.Tester = Tester

    def test_that_it_supports_calls_from_instances(self):
        Tester = self.Tester 

        with self.assertRaises(AttributeError):
            Tester().special_method() 

        self.assertEqual(Tester.special_method(), Tester)

    def test_that_it_has_classmethod_behavior(self):
        class SpecificTester(self.Tester):
            'Just a sublcass to prove it.'

        self.assertEqual(SpecificTester.special_method(), SpecificTester)


class CachedPropertyTest(unittest.TestCase):
    def setUp(self):
        class Tester(object):
            def timer(self):
                return time.time()

            cached_timer = cachedproperty(timer) 
            regular_timer = property(timer) 

        self.Tester = Tester

    def test_that_it_memoizes(self):
        tester = self.Tester()

        initial_cached = tester.cached_timer
        initial_regular = tester.regular_timer

        time.sleep(0.1) # Force the time - kinda ugly, but meh...

        self.assertTrue(initial_cached == tester.cached_timer)
        self.assertTrue(tester.cached_timer == tester.cached_timer)
        self.assertFalse(initial_regular == tester.regular_timer)


class IdentityTest(unittest.TestCase):
    def test_that_it_returns_itself(self):
        self.assertTrue(identity(True) is True)
        self.assertTrue(identity(object) is object)


class TryInOrderTest(unittest.TestCase):
    def test_that_it_returns_the_first_successful_function(self):
        self.assertTrue(try_in_order(lambda: True) == True)
        self.assertTrue(try_in_order(lambda: 1 / 0, lambda: True) == True)

    def test_that_it_delegates_function_arguments(self):
        self.assertTrue(try_in_order(lambda a : a / 0, lambda a: [a][0],
                                     args=[1])  == 1)

    def test_that_it_preserves_the_last_stacktrace(self):
        with self.assertRaises(IndexError):
            try_in_order(lambda: 1/0, lambda: [][0])


class SentinelTest(unittest.TestCase):
    def test_that_it_is_falsy(self):
        self.assertFalse(bool(Sentinel))
