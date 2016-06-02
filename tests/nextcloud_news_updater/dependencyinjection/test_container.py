from unittest import TestCase

from nextcloud_news_updater.dependencyinjection.container import Container


class A:
    pass


class B:
    def __init__(self, param: A):
        self.param = param


class C:
    def __init__(self, param: B):
        self.param = param


class TestContainer(TestCase):
    def setUp(self):
        self.container = Container()

    def test_register(self):
        self.container.register(A, lambda c: 'swapped out')
        self.assertEqual('swapped out', self.container.resolve(B).param)

    def test_resolve(self):
        a = self.container.resolve(A)
        self.assertIsInstance(a, A)

        b = self.container.resolve(B)
        self.assertIsInstance(b, B)
        self.assertIsInstance(b.param, A)

    def test_resolve_shared(self):
        self.container.register(A, lambda c: A(), False)

        a1 = self.container.resolve(A)
        a2 = self.container.resolve(A)
        self.assertIsInstance(a1, A)
        self.assertIsInstance(a2, A)
        self.assertNotEqual(a1, a2)

    def test_alias(self):
        self.container.alias(A, B)
        a = self.container.resolve(B)
        self.assertIsInstance(a, A)

        c = self.container.resolve(C)
        self.assertIsInstance(c, C)
        self.assertIsInstance(c.param, A)
