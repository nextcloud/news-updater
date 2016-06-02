import json
from unittest import TestCase
from unittest.mock import MagicMock, call

from nextcloud_news_updater.api.updater import Updater
from nextcloud_news_updater.api.cli import Cli, CliApi, CliApiV2
from nextcloud_news_updater.config import Config
from nextcloud_news_updater.container import Container


class TestCli(TestCase):
    def setUp(self):
        self.container = Container()
        self.cli = MagicMock(spec=Cli)
        self.container.register(Cli, lambda c: self.cli)
        self.base_url = '/'
        self.phpini = '/path/to/ini'

    def _set_config(self, **kwargs):
        config = Config()
        for key, value in kwargs.items():
            setattr(config, key, value)
        self.container.register(Config, lambda c: config)

    def _set_cli_run(self, return_value):
        attrs = {'run.return_value': bytes(json.dumps(return_value), 'utf-8')}
        self.cli.configure_mock(**attrs)

    def test_api_level(self):
        self._set_config(apilevel='v1-2', url=self.base_url)
        api = self.container.resolve(CliApi)
        self.assertIsInstance(api, CliApi)

    def test_api_level_v2(self):
        self._set_config(apilevel='v2', url=self.base_url)
        api = self.container.resolve(CliApi)
        self.assertIsInstance(api, CliApiV2)

    def _create_commands(self, phpini_path=None):
        if phpini_path:
            phpini_cmd = ['-c', phpini_path]
        else:
            phpini_cmd = []
        base_cmd = ['php', '-f', '%socc' % self.base_url] + phpini_cmd
        before_cmd = base_cmd + ['news:updater:before-update']
        feeds_cmd = base_cmd + ['news:updater:all-feeds']
        update_cmd1 = base_cmd + ['news:updater:update-feed', '2', 'deb']
        update_cmd2 = base_cmd + ['news:updater:update-feed', '3', 'john']
        after_cmd = base_cmd + ['news:updater:after-update']

        # ordering can be switched due to threading, so try both cases
        return ([call(before_cmd), call(feeds_cmd), call(update_cmd1),
                 call(update_cmd2), call(after_cmd)],
                [call(before_cmd), call(feeds_cmd), call(update_cmd2),
                 call(update_cmd1), call(after_cmd)])

    def test_api_v1_calls(self):
        self._set_config(apilevel='v1-2', url=self.base_url, mode='singlerun')
        updater = self.container.resolve(Updater)
        self._set_cli_run({
            'feeds': [{'id': 3, 'userId': 'john'}, {'id': 2, 'userId': 'deb'}]
        })
        updater.run()
        self.assertIn(self.cli.run.call_args_list, self._create_commands())

    def test_api_v2_calls(self):
        self._set_config(apilevel='v2', url=self.base_url, mode='singlerun')
        updater = self.container.resolve(Updater)
        self._set_cli_run({
            'updater': [{'feedId': 3, 'userId': 'john'},
                        {'feedId': 2, 'userId': 'deb'}]
        })
        updater.run()

        self.assertIn(self.cli.run.call_args_list, self._create_commands())

    def test_api_v2_calls_phpini(self):
        self._set_config(apilevel='v2', url=self.base_url, mode='singlerun',
                         phpini=self.phpini)
        updater = self.container.resolve(Updater)
        self._set_cli_run({
            'updater': [{'feedId': 3, 'userId': 'john'},
                        {'feedId': 2, 'userId': 'deb'}]
        })
        updater.run()

        self.assertIn(self.cli.run.call_args_list,
                      self._create_commands(self.phpini))

    def test_api_v1_calls_phpini(self):
        self._set_config(apilevel='v1-2', url=self.base_url, mode='singlerun',
                         phpini=self.phpini)
        updater = self.container.resolve(Updater)
        self._set_cli_run({
            'feeds': [{'id': 3, 'userId': 'john'}, {'id': 2, 'userId': 'deb'}]
        })
        updater.run()
        self.assertIn(self.cli.run.call_args_list,
                      self._create_commands(self.phpini))
