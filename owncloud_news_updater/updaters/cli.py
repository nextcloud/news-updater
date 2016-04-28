from subprocess import check_output

from owncloud_news_updater.updaters.facades import parse_json
from owncloud_news_updater.updaters.updater import Updater, UpdateThread


class ConsoleUpdater(Updater):
    def __init__(self, directory, thread_num, interval, run_once, log_level):
        super().__init__(thread_num, interval, run_once, log_level)
        self.directory = directory.rstrip('/')
        base_command = ['php', '-f', self.directory + '/occ']
        self.before_cleanup_command = base_command + [
            'news:updater:before-update']
        self.all_feeds_command = base_command + ['news:updater:all-feeds']
        self.update_feed_command = base_command + ['news:updater:update-feed']
        self.after_cleanup_command = base_command + [
            'news:updater:after-update']

    def before_update(self):
        self.logger.info('Running before update command %s' %
                         ' '.join(self.before_cleanup_command))
        check_output(self.before_cleanup_command)

    def start_update_thread(self, feeds):
        return ConsoleUpdateThread(feeds, self.logger,
                                   self.update_feed_command)

    def all_feeds(self):
        feeds_json = check_output(self.all_feeds_command).strip()
        feeds_json = str(feeds_json, 'utf-8')
        self.logger.info('Received these feeds to update: %s' % feeds_json)
        return parse_json(feeds_json)['feeds']

    def after_update(self):
        self.logger.info('Running after update command %s' %
                         ' '.join(self.after_cleanup_command))
        check_output(self.before_cleanup_command)


class ConsoleUpdateThread(UpdateThread):
    def __init__(self, feeds, logger, update_base_command):
        super().__init__(feeds, logger)
        self.update_base_command = update_base_command

    def update_feed(self, feed):
        command = self.update_base_command + [str(feed['id']), feed['userId']]
        self.logger.info('Running update command %s' % ' '.join(command))
        check_output(command)
