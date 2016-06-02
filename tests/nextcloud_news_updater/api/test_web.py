import json
from unittest import TestCase
from unittest.mock import MagicMock, call

from nextcloud_news_updater.api.updater import Updater
from nextcloud_news_updater.api.web import HttpClient, WebApi, WebApiV2
from nextcloud_news_updater.config import Config
from nextcloud_news_updater.container import Container


class TestWeb(TestCase):
    def setUp(self):
        self.container = Container()
        self.http = MagicMock(spec=HttpClient)
        self.container.register(HttpClient, lambda c: self.http)
        self.base_url = 'http://google.de'

    def _set_config(self, **kwargs):
        config = Config()
        for key, value in kwargs.items():
            setattr(config, key, value)
        self.container.register(Config, lambda c: config)

    def _set_http_get(self, return_value):
        attrs = {'get.return_value': json.dumps(return_value)}
        self.http.configure_mock(**attrs)

    def test_api_level(self):
        self._set_config(apilevel='v1-2', url=self.base_url)
        api = self.container.resolve(WebApi)
        self.assertIsInstance(api, WebApi)

    def test_api_level_v2(self):
        self._set_config(apilevel='v2', url=self.base_url)
        api = self.container.resolve(WebApi)
        self.assertIsInstance(api, WebApiV2)

    def _create_urls_v1(self):
        before_url = '%s/index.php/apps/news/api/v1-2/cleanup/before-update' \
                     % self.base_url
        feeds_url = '%s/index.php/apps/news/api/v1-2/feeds/all' \
                    % self.base_url
        update_url1 = '%s/index.php/apps/news/api/v1-2/feeds/update' \
                      '?userId=deb&feedId=2' % self.base_url
        update_url2 = '%s/index.php/apps/news/api/v1-2/feeds/update' \
                      '?userId=john&feedId=3' % self.base_url
        after_url = '%s/index.php/apps/news/api/v1-2/cleanup/after-update' \
                    % self.base_url
        auth = ('john', 'pass')
        timeout = 5 * 60

        # ordering can be switched due to threading, so try both cases
        return ([call(before_url, auth), call(feeds_url, auth),
                 call(update_url1, auth, timeout),
                 call(update_url2, auth, timeout), call(after_url, auth)],
                [call(before_url, auth), call(feeds_url, auth),
                 call(update_url2, auth, timeout),
                 call(update_url1, auth, timeout), call(after_url, auth)])

    def _create_urls_v2(self):
        before_url = '%s/index.php/apps/news/api/v2/updater/before-update' \
                     % self.base_url
        feeds_url = '%s/index.php/apps/news/api/v2/updater/all-feeds' \
                    % self.base_url
        update_url1 = '%s/index.php/apps/news/api/v2/updater/update-feed' \
                      '?userId=deb&feedId=2' % self.base_url
        update_url2 = '%s/index.php/apps/news/api/v2/updater/update-feed' \
                      '?userId=john&feedId=3' % self.base_url
        after_url = '%s/index.php/apps/news/api/v2/updater/after-update' \
                    % self.base_url
        auth = ('john', 'pass')
        timeout = 5 * 60

        # ordering can be switched due to threading, so try both cases
        return ([call(before_url, auth), call(feeds_url, auth),
                 call(update_url1, auth, timeout),
                 call(update_url2, auth, timeout), call(after_url, auth)],
                [call(before_url, auth), call(feeds_url, auth),
                 call(update_url2, auth, timeout),
                 call(update_url1, auth, timeout), call(after_url, auth)])

    def test_api_v1_calls(self):
        self._set_config(apilevel='v1-2', url=self.base_url, user='john',
                         password='pass', mode='singlerun')
        updater = self.container.resolve(Updater)
        self._set_http_get({
            'feeds': [{'id': 3, 'userId': 'john'}, {'id': 2, 'userId': 'deb'}]
        })
        updater.run()
        self.assertIn(self.http.get.call_args_list, self._create_urls_v1())

    def test_api_v2_calls(self):
        self._set_config(apilevel='v2', url=self.base_url, user='john',
                         password='pass', mode='singlerun')
        updater = self.container.resolve(Updater)
        self._set_http_get({
            'updater': [{'feedId': 3, 'userId': 'john'},
                        {'feedId': 2, 'userId': 'deb'}]
        })
        updater.run()
        self.assertIn(self.http.get.call_args_list, self._create_urls_v2())
