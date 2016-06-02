from unittest import TestCase
from configparser import MissingSectionHeaderError

from nextcloud_news_updater.common.argumentparser import ArgumentParser
from nextcloud_news_updater.config import InvalidConfigException, \
    ConfigParser, merge_configs, ConfigValidator, InvalidConfigKeyException, \
    Config
from nextcloud_news_updater.container import Container
from tests.nextcloud_news_updater import find_test_config, assert_raises


class Args:
    def __init__(self):
        self.user = 'john'
        self.threads = 100
        self.config = None

    def parse(self):
        return self

    def print_help(self, file):
        pass


class TestConfig(TestCase):
    def setUp(self):
        self.parser = ConfigParser()
        self.container = Container()

    def test_parse_full(self):
        config = self.parser.parse_file(find_test_config('full.ini'))
        self.assertEqual(config.user, 'admin')
        self.assertEqual(config.password, 'pass')
        self.assertEqual(config.threads, 2)
        self.assertEqual(config.interval, 9)
        self.assertEqual(config.loglevel, 'info')
        self.assertEqual(config.url, '/')
        self.assertEqual(config.phpini, '/path/to/custom/php.ini')
        self.assertEqual(config.apilevel, 'v2')
        self.assertEqual(config.mode, 'singlerun')

    def test_parse_defaults(self):
        config = self.parser.parse_file(find_test_config('empty.ini'))
        self.assertEqual(config.loglevel, 'error')
        self.assertEqual(config.interval, 15 * 60)
        self.assertEqual(config.timeout, 5 * 60)
        self.assertEqual(config.apilevel, 'v1-2')
        self.assertEqual(config.threads, 10)
        self.assertEqual(config.mode, 'endless')
        self.assertEqual(config.user, None)
        self.assertEqual(config.password, '')
        self.assertEqual(config.url, None)
        self.assertEqual(config.phpini, None)

    def test_merge_configs(self):
        config = self.parser.parse_file(find_test_config('full.ini'))
        merge_configs(Args(), config)
        self.assertEqual(config.user, 'john')
        self.assertEqual(config.password, 'pass')
        self.assertEqual(config.threads, 100)
        self.assertEqual(config.interval, 9)
        self.assertEqual(config.loglevel, 'info')
        self.assertEqual(config.url, '/')
        self.assertEqual(config.phpini, '/path/to/custom/php.ini')
        self.assertEqual(config.apilevel, 'v2')
        self.assertEqual(config.mode, 'singlerun')

    def test_validate_config_empty_url(self):
        config = self.parser.parse_file(find_test_config('empty.ini'))
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual(['No url given'], result)

    def test_validate_config_relative_url(self):
        config = self.parser.parse_file(find_test_config('empty.ini'))
        config.url = 'relative/path'
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual(['Absolute path or full Url required'], result)

    def test_validate_config_url_no_user(self):
        config = self.parser.parse_file(find_test_config('empty.ini'))
        config.url = 'https://google.com/'
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual(['Url given but no user present'], result)

    def test_validate_config_no_directory(self):
        config = self.parser.parse_file(find_test_config('empty.ini'))
        config.url = '/blububuubbububu'
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual(['Given path is not a directory'], result)

    def test_validate_invalid_mode(self):
        config = self.parser.parse_file(find_test_config('full.ini'))
        config.mode = 'singleru'
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual(['Unknown mode: singleru'], result)

    def test_validate_invalid_apilevel(self):
        config = self.parser.parse_file(find_test_config('full.ini'))
        config.apilevel = 'v1-3'
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual(['Unknown apilevel: v1-3'], result)

    def test_validate_invalid_loglevel(self):
        config = self.parser.parse_file(find_test_config('full.ini'))
        config.loglevel = 'debug'
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual(['Unknown loglevel: debug'], result)

    def test_validate_invalid_phpini(self):
        config = self.parser.parse_file(find_test_config('full.ini'))
        config.phpini = 'php.ini'
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual(['Path to php.ini must be absolute'], result)

    def test_validate_ok(self):
        config = self.parser.parse_file(find_test_config('full.ini'))
        validator = ConfigValidator()
        result = validator.validate(config)
        self.assertListEqual([], result)

    @assert_raises(MissingSectionHeaderError)
    def test_load_fails(self):
        self.parser.parse_file(find_test_config('invalid.ini'))

    @assert_raises(InvalidConfigException)
    def test_load_fails(self):
        self.parser.parse_file(find_test_config('notexisting.ini'))

    @assert_raises(InvalidConfigKeyException)
    def test_load_fails(self):
        self.parser.parse_file(find_test_config('unknown_key.ini'))

    def test_integration_merge(self):
        args = Args()
        args.config = find_test_config('full.ini')
        self.container.register(ArgumentParser, lambda c: args)
        config = self.container.resolve(Config)
        self.assertEqual(config.user, 'john')
        self.assertEqual(config.password, 'pass')
        self.assertEqual(config.threads, 100)
        self.assertEqual(config.interval, 9)
        self.assertEqual(config.loglevel, 'info')
        self.assertEqual(config.url, '/')
        self.assertEqual(config.phpini, '/path/to/custom/php.ini')
        self.assertEqual(config.apilevel, 'v2')
        self.assertEqual(config.mode, 'singlerun')
