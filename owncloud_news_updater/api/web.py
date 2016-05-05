import base64
import urllib.parse
import urllib.request

from owncloud_news_updater.api.api import Api, Feed
from owncloud_news_updater.api.updater import Updater, UpdateThread
from owncloud_news_updater.common.logger import Logger
from owncloud_news_updater.config import Config


class WebApi(Api):
    def __init__(self, config):
        base_url = config.url
        base_url = self._generify_base_url(base_url)
        self.base_url = '%sindex.php/apps/news/api/v1-2' % base_url
        self.before_cleanup_url = '%s/cleanup/before-update' % self.base_url
        self.after_cleanup_url = '%s/cleanup/after-update' % self.base_url
        self.all_feeds_url = '%s/feeds/all' % self.base_url
        self.update_url = '%s/feeds/update' % self.base_url

    def _generify_base_url(self, url):
        if not url.endswith('/'):
            url += '/'
        return url


class WebApiV2(WebApi):
    def __init__(self, config):
        super().__init__(config)
        base_url = self._generify_base_url(config.url)
        self.base_url = '%sindex.php/apps/news/api/v2' % base_url
        self.before_cleanup_url = '%s/updater/before-update' % self.base_url
        self.after_cleanup_url = '%s/updater/after-update' % self.base_url
        self.all_feeds_url = '%s/updater/all-feeds' % self.base_url
        self.update_url = '%s/updater/update-feed' % self.base_url

    def _parse_json(self, feed_json):
        feed_json = feed_json['data']['updater']
        return [Feed(info['feedId'], info['userId']) for info in feed_json]


def create_web_api(config):
    if config.apilevel == 'v1-2':
        return WebApi(config)
    if config.apilevel == 'v2':
        return WebApiV2(config)


class HttpClient:
    def get(self, url, auth, timeout=5 * 60):
        """
        Small wrapper for getting rid of the requests library
        """
        auth = bytes(auth[0] + ':' + auth[1], 'utf-8')
        auth_header = 'Basic ' + base64.b64encode(auth).decode('utf-8')
        req = urllib.request.Request(url)
        req.add_header('Authorization', auth_header)
        response = urllib.request.urlopen(req, timeout=timeout)
        return response.read().decode('utf8')


class WebUpdater(Updater):
    def __init__(self, config: Config, logger: Logger, api: WebApi,
                 client: HttpClient):
        super().__init__(config, logger)
        self.client = client
        self.api = api
        self.auth = (config.user, config.password)

    def before_update(self):
        self.logger.info(
            'Calling before update url:  %s' % self.api.before_cleanup_url)
        self.client.get(self.api.before_cleanup_url, self.auth)

    def start_update_thread(self, feeds):
        return WebUpdateThread(feeds, self.config, self.logger, self.api,
                               self.client)

    def all_feeds(self):
        feeds_json = self.client.get(self.api.all_feeds_url, self.auth)
        self.logger.info('Received these feeds to update: %s' % feeds_json)
        return self.api.parse_feed(feeds_json)

    def after_update(self):
        self.logger.info(
            'Calling after update url:  %s' % self.api.after_cleanup_url)
        self.client.get(self.api.after_cleanup_url, self.auth)


class WebUpdateThread(UpdateThread):
    def __init__(self, feeds, config, logger, api, client):
        super().__init__(feeds, logger)
        self.client = client
        self.api = api
        self.auth = (config.user, config.password)
        self.config = config

    def update_feed(self, feed):
        data = {
            'feedId': feed.feed_id,
            'userId': feed.user_id
        }
        data = urllib.parse.urlencode(data)
        url = '%s?%s' % (self.api.update_url, data)
        self.logger.info('Calling update url: %s' % url)
        self.client.get(url, self.auth, self.config.timeout)
