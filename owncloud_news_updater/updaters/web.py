import urllib.parse

from owncloud_news_updater.updaters.facades import http_get, parse_json
from owncloud_news_updater.updaters.updater import Updater, UpdateThread


class WebUpdater(Updater):
    def __init__(self, base_url, thread_num, interval, run_once,
                 user, password, timeout, log_level):
        super().__init__(thread_num, interval, run_once, log_level)
        self.base_url = base_url
        self.auth = (user, password)
        self.timeout = timeout

        if self.base_url[-1] != '/':
            self.base_url += '/'
        self.base_url += 'index.php/apps/news/api/v1-2'

        self.before_cleanup_url = '%s/cleanup/before-update' % self.base_url
        self.after_cleanup_url = '%s/cleanup/after-update' % self.base_url
        self.all_feeds_url = '%s/feeds/all' % self.base_url
        self.update_url = '%s/feeds/update' % self.base_url

    def before_update(self):
        self.logger.info(
            'Calling before update url:  %s' % self.before_cleanup_url)
        http_get(self.before_cleanup_url, auth=self.auth)

    def start_update_thread(self, feeds):
        return WebUpdateThread(feeds, self.logger, self.update_url, self.auth,
                               self.timeout)

    def all_feeds(self):
        feeds_json = http_get(self.all_feeds_url, auth=self.auth)
        self.logger.info('Received these feeds to update: %s' % feeds_json)
        return parse_json(feeds_json)['feeds']

    def after_update(self):
        self.logger.info(
            'Calling after update url:  %s' % self.after_cleanup_url)
        http_get(self.after_cleanup_url, auth=self.auth)


class WebUpdateThread(UpdateThread):
    def __init__(self, feeds, logger, update_url, auth, timeout):
        super().__init__(feeds, logger)
        self.update_url = update_url
        self.auth = auth
        self.timeout = timeout

    def update_feed(self, feed):
        # rewrite parameters, a feeds id is mapped to feedId
        feed['feedId'] = feed['id']
        del feed['id']

        # turn the pyton dict into url parameters
        data = urllib.parse.urlencode(feed)
        url = '%s?%s' % (self.update_url, data)
        http_get(url, auth=self.auth, timeout=self.timeout)
