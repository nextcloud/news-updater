import base64
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from collections import OrderedDict
from typing import List, Tuple, Any

from nextcloud_news_updater.api.api import Api, Feed
from nextcloud_news_updater.api.updater import Updater, UpdateThread
from nextcloud_news_updater.common.logger import Logger
from nextcloud_news_updater.config import Config


class WebApi(Api):
    def __init__(self, config: Config) -> None:
        base_url = config.url
        base_url = self._generify_base_url(base_url)
        self.base_url = '%sindex.php/apps/news/api/v1-2' % base_url
        self.before_cleanup_url = '%s/cleanup/before-update' % self.base_url
        self.after_cleanup_url = '%s/cleanup/after-update' % self.base_url
        self.all_feeds_url = '%s/feeds/all' % self.base_url
        self.update_url = '%s/feeds/update' % self.base_url

    def _generify_base_url(self, url: str) -> str:
        if not url.endswith('/'):
            url += '/'
        return url


class WebApiV2(WebApi):
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        base_url = self._generify_base_url(config.url)
        self.base_url = '%sindex.php/apps/news/api/v2' % base_url
        self.before_cleanup_url = '%s/updater/before-update' % self.base_url
        self.after_cleanup_url = '%s/updater/after-update' % self.base_url
        self.all_feeds_url = '%s/updater/all-feeds' % self.base_url
        self.update_url = '%s/updater/update-feed' % self.base_url

    def _parse_json(self, feed_json: Any) -> List[Feed]:
        feed_json = feed_json['updater']
        return [Feed(info['feedId'], info['userId']) for info in feed_json]


def create_web_api(config: Config) -> WebApi:
    if config.apilevel == 'v1-2':
        return WebApi(config)
    if config.apilevel == 'v2':
        return WebApiV2(config)


class HttpClient:
    def get(self, url: str, auth: Tuple[str, str],
            timeout: int = 5 * 60) -> str:
        """
        Small wrapper for getting rid of the requests library
        """
        basic_auth = bytes(':'.join(auth), 'utf-8')
        auth_header = 'Basic ' + base64.b64encode(basic_auth).decode('utf-8')
        req = Request(url)
        req.add_header('Authorization', auth_header)
        response = urlopen(req, timeout=timeout)
        return response.read().decode('utf8')


class WebUpdater(Updater):
    def __init__(self, config: Config, logger: Logger, api: WebApi,
                 client: HttpClient) -> None:
        super().__init__(config, logger)
        self.client = client
        self.api = api
        self.auth = (config.user, config.password)

    def before_update(self) -> None:
        self.logger.info(
            'Calling before update url:  %s' % self.api.before_cleanup_url)
        self.client.get(self.api.before_cleanup_url, self.auth)

    def start_update_thread(self, feeds: List[Feed]) -> UpdateThread:
        return WebUpdateThread(feeds, self.config, self.logger, self.api,
                               self.client)

    def all_feeds(self) -> List[Feed]:
        feeds_json = self.client.get(self.api.all_feeds_url, self.auth)
        self.logger.info('Received these feeds to update: %s' % feeds_json)
        return self.api.parse_feed(feeds_json)

    def after_update(self) -> None:
        self.logger.info(
            'Calling after update url:  %s' % self.api.after_cleanup_url)
        self.client.get(self.api.after_cleanup_url, self.auth)


class WebUpdateThread(UpdateThread):
    def __init__(self, feeds: List[Feed], config: Config, logger: Logger,
                 api: WebApi, client: HttpClient) -> None:
        super().__init__(feeds, logger)
        self.client = client
        self.api = api
        self.auth = (config.user, config.password)
        self.config = config

    def update_feed(self, feed: Feed) -> None:
        # make sure that the order is always defined for making it easier
        # to test and reason about, normal dicts are not ordered
        data = OrderedDict([
            ('userId', feed.user_id),
            ('feedId', str(feed.feed_id)),
        ])
        url_data = urlencode(data)
        url = '%s?%s' % (self.api.update_url, url_data)
        self.logger.info('Calling update url: %s' % url)
        self.client.get(url, self.auth, self.config.timeout)
