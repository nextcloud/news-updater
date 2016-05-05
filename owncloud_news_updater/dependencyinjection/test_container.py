from unittest import TestCase

from owncloud_news_updater.dependencyinjection.container import Container


class A:
    pass


class B:
    def __init__(self, param: A):
        self.param = param


class C:
    def __init__(self, param: B):
        self.param = param


class ContainerTest(TestCase):
    def test_register(self):
        container = Container()
        container.register(A, lambda c: 'swapped out')
        self.assertEqual('swapped out', container.resolve(B).param)

    def test_resolve(self):
        container = Container()
        a = container.resolve(A)
        self.assertIsInstance(a, A)

        b = container.resolve(B)
        self.assertIsInstance(b, B)
        self.assertIsInstance(b.param, A)

    def test_resolve_shared(self):
        container = Container()
        container.register(A, lambda c: A(), False)

        a1 = container.resolve(A)
        a2 = container.resolve(A)
        self.assertIsInstance(a1, A)
        self.assertIsInstance(a2, A)
        self.assertNotEqual(a1, a2)

    def test_alias(self):
        container = Container()
        container.alias(A, B)
        a = container.resolve(B)
        self.assertIsInstance(a, A)

        c = container.resolve(C)
        self.assertIsInstance(c, C)
        self.assertIsInstance(c.param, A)
