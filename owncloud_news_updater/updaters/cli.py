from subprocess import check_output

from owncloud_news_updater.updaters.api import Api
from owncloud_news_updater.updaters.updater import Updater, UpdateThread


class CliUpdater(Updater):
    def __init__(self, thread_num, interval, run_once, log_level, api):
        super().__init__(thread_num, interval, run_once, log_level)
        self.api = api

    def before_update(self):
        self.logger.info('Running before update command %s' %
                         ' '.join(self.api.before_cleanup_command))
        check_output(self.api.before_cleanup_command)

    def start_update_thread(self, feeds):
        return CliUpdateThread(feeds, self.logger,
                               self.api)

    def all_feeds(self):
        feeds_json = check_output(self.api.all_feeds_command).strip()
        feeds_json = str(feeds_json, 'utf-8')
        self.logger.info('Received these feeds to update: %s' % feeds_json)
        return self.api.parse_feed(feeds_json)

    def after_update(self):
        self.logger.info('Running after update command %s' %
                         ' '.join(self.api.after_cleanup_command))
        check_output(self.api.before_cleanup_command)


class CliUpdateThread(UpdateThread):
    def __init__(self, feeds, logger, api):
        super().__init__(feeds, logger)
        self.api = api

    def update_feed(self, feed):
        command = self.api.update_base_command + [str(feed.feedId),
                                                  feed.userId]
        self.logger.info('Running update command %s' % ' '.join(command))
        check_output(command)


class CliApi(Api):
    def __init__(self, directory):
        self.directory = directory.rstrip('/')
        base_command = ['php', '-f', self.directory + '/occ']
        self.before_cleanup_command = base_command + [
            'news:updater:before-update']
        self.all_feeds_command = base_command + ['news:updater:all-feeds']
        self.update_feed_command = base_command + ['news:updater:update-feed']
        self.after_cleanup_command = base_command + [
            'news:updater:after-update']
