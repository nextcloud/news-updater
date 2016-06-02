from subprocess import check_output
from typing import List, Any

from nextcloud_news_updater.api.api import Api, Feed
from nextcloud_news_updater.api.updater import Updater, UpdateThread
from nextcloud_news_updater.common.logger import Logger
from nextcloud_news_updater.config import Config


class Cli:
    def run(self, commands: List[str]) -> bytes:
        return check_output(commands)


class CliApi(Api):
    def __init__(self, config: Config) -> None:
        directory = config.url
        phpini = config.phpini
        if not directory.endswith('/'):
            directory += '/'
        self.directory = directory
        base_command = ['php', '-f', self.directory + 'occ']
        if phpini is not None and phpini.strip() != '':
            base_command += ['-c', phpini]
        self.before_cleanup_command = base_command + [
            'news:updater:before-update']
        self.all_feeds_command = base_command + ['news:updater:all-feeds']
        self.update_feed_command = base_command + ['news:updater:update-feed']
        self.after_cleanup_command = base_command + [
            'news:updater:after-update']


class CliApiV2(CliApi):
    def __init__(self, config: Config) -> None:
        super().__init__(config)

    def _parse_json(self, feed_json: Any) -> List[Feed]:
        feed_json = feed_json['updater']
        return [Feed(info['feedId'], info['userId']) for info in feed_json]


def create_cli_api(config: Config) -> CliApi:
    if config.apilevel == 'v1-2':
        return CliApi(config)
    if config.apilevel == 'v2':
        return CliApiV2(config)


class CliUpdateThread(UpdateThread):
    def __init__(self, feeds: List[Feed], logger: Logger, api: CliApi,
                 cli: Cli) -> None:
        super().__init__(feeds, logger)
        self.cli = cli
        self.api = api

    def update_feed(self, feed: Feed) -> None:
        command = self.api.update_feed_command + [str(feed.feed_id),
                                                  feed.user_id]
        self.logger.info('Running update command: %s' % ' '.join(command))
        self.cli.run(command)


class CliUpdater(Updater):
    def __init__(self, config: Config, logger: Logger, api: CliApi,
                 cli: Cli) -> None:
        super().__init__(config, logger)
        self.cli = cli
        self.api = api

    def before_update(self) -> None:
        self.logger.info('Running before update command: %s' %
                         ' '.join(self.api.before_cleanup_command))
        self.cli.run(self.api.before_cleanup_command)

    def start_update_thread(self, feeds: List[Feed]) -> CliUpdateThread:
        return CliUpdateThread(feeds, self.logger, self.api, self.cli)

    def all_feeds(self) -> List[Feed]:
        feeds_json_bytes = self.cli.run(self.api.all_feeds_command).strip()
        feeds_json = str(feeds_json_bytes, 'utf-8')
        self.logger.info('Running get all feeds command: %s' %
                         ' '.join(self.api.all_feeds_command))
        self.logger.info('Received these feeds to update: %s' % feeds_json)
        return self.api.parse_feed(feeds_json)

    def after_update(self) -> None:
        self.logger.info('Running after update command: %s' %
                         ' '.join(self.api.after_cleanup_command))
        self.cli.run(self.api.after_cleanup_command)
