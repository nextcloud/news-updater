import unittest
from owncloud_news_updater.updaters.cli import CliApi


class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        cli = CliApi('test', None)
        self.assertEqual('foo'.upper(), 'FOO')
