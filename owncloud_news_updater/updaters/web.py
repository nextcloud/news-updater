import base64
import urllib.parse
import urllib.request

from owncloud_news_updater.updaters.api import Api, Feed
from owncloud_news_updater.updaters.updater import Updater, UpdateThread


def http_get(url, auth, timeout=5 * 60):
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
    def __init__(self, thread_num, interval, run_once, log_level, timeout, api,
                 user, password):
        super().__init__(thread_num, interval, run_once, log_level)
        self.api = api
        self.auth = (user, password)
        self.timeout = timeout

    def before_update(self):
        self.logger.info(
            'Calling before update url:  %s' % self.api.before_cleanup_url)
        http_get(self.api.before_cleanup_url, auth=self.auth)

    def start_update_thread(self, feeds):
        return WebUpdateThread(feeds, self.logger, self.api,
                               self.auth, self.timeout)

    def all_feeds(self):
        feeds_json = http_get(self.api.all_feeds_url, auth=self.auth)
        self.logger.info('Received these feeds to update: %s' % feeds_json)
        return self.api.parse_feed(feeds_json)

    def after_update(self):
        self.logger.info(
            'Calling after update url:  %s' % self.api.after_cleanup_url)
        http_get(self.api.after_cleanup_url, auth=self.auth)


class WebUpdateThread(UpdateThread):
    def __init__(self, feeds, logger, api, auth, timeout):
        super().__init__(feeds, logger)
        self.api = api
        self.auth = auth
        self.timeout = timeout

    def update_feed(self, feed):
        data = {
            'feedId': feed.feedId,
            'userId': feed.userId
        }
        data = urllib.parse.urlencode(data)
        url = '%s?%s' % (self.api.update_url, data)
        self.logger.info('Calling update url: %s' % url)
        http_get(url, auth=self.auth, timeout=self.timeout)


class WebApi(Api):
    def __init__(self, base_url):
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
    def __init__(self, base_url):
        super().__init__(base_url)
        base_url = self._generify_base_url(base_url)
        self.base_url = '%sindex.php/apps/news/api/v2' % base_url
        self.before_cleanup_url = '%s/updater/before-update' % self.base_url
        self.after_cleanup_url = '%s/updater/after-update' % self.base_url
        self.all_feeds_url = '%s/updater/all-feeds' % self.base_url
        self.update_url = '%s/updater/update-feed' % self.base_url

    def _parse_json(self, feed_json):
        feed_json = feed_json['data']['updater']
        return [Feed(info['feedId'], info['userId']) for info in feed_json]

def create_web_api(api_level, url):
    if api_level == 'v1-2':
        return WebApi(url)
    if api_level == 'v2':
        return WebApiV2(url)