from subprocess import check_output, CalledProcessError, STDOUT
from typing import List, Any

from nextcloud_news_updater.api.api import Api, Feed
from nextcloud_news_updater.api.updater import Updater, UpdateThread
from nextcloud_news_updater.common.logger import Logger
from nextcloud_news_updater.config import Config


class Cli:
    def run(self, commands: List[str]) -> bytes:
        return check_output(commands, stderr=STDOUT)


class CliApi(Api):
    """Cli API for Nextcloud News up to v14 (API version 1.2)"""

    def __init__(self, config: Config) -> None:
        directory = config.url
        phpini = config.phpini
        if not directory.endswith('/'):
            directory += '/'
        self.directory = directory
        self.base_command = [config.php, '-f', self.directory + 'occ']
        if phpini is not None and phpini.strip() != '':
            self.base_command += ['-c', phpini]
        self.before_cleanup_command = self.base_command + [
            'news:updater:before-update']
        self.all_feeds_command = self.base_command + [
            'news:updater:all-feeds']
        self.update_feed_command = self.base_command + [
            'news:updater:update-feed']
        self.after_cleanup_command = self.base_command + [
            'news:updater:after-update']


class CliApiV2(CliApi):
    """Cli API for Nextcloud News up to v14 (API version 2)"""

    def _parse_feeds_json(self, feeds: dict, userID: str) -> List[Feed]:
        feeds = feeds['updater']
        return [Feed(info['feedId'], info['userId']) for info in feeds]


class CliApiV15(CliApi):
    """Cli API for Nextcloud News v15+"""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.all_feeds_command = self.base_command + ['news:feed:list']
        self.users_list_command = self.base_command + ['user:list', '--output',
                                                       'json']

    def _parse_feeds_json(self, feeds_json: Any, userID: str) -> List[Feed]:
        if not feeds_json:
            return []
        return [Feed(info['id'], userID) for info in feeds_json]


def create_cli_api(config: Config) -> CliApi:
    if config.apilevel == 'v1-2':
        return CliApi(config)
    if config.apilevel == 'v2':
        return CliApiV2(config)
    if config.apilevel == 'v15':
        return CliApiV15(config)


class CliUpdateThread(UpdateThread):
    def __init__(self, feeds: List[Feed], logger: Logger, api: CliApi,
                 cli: Cli) -> None:
        super().__init__(feeds, logger)
        self.cli = cli
        self.api = api

    def run_command(self, command: List[str]) -> None:
        self.logger.info('Running update command: %s' % ' '.join(command))
        try:
            self.cli.run(command)
        except CalledProcessError as e:
            self.logger.error("Command '%s' returned %d with output: '%s'" %
                              (' '. join(command),
                               e.returncode,
                               e.output.decode().strip()))

    def update_feed(self, feed: Feed) -> None:
        command = self.api.update_feed_command + [str(feed.feed_id),
                                                  feed.user_id]
        self.run_command(command)

class CliUpdateThreadV15(CliUpdateThread):
    """Cli Updater for Nextcloud News v15+"""

    def update_feed(self, feed: Feed) -> None:
        command = self.api.update_feed_command + [feed.user_id,
                                                  str(feed.feed_id)]
        self.run_command(command)

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
        return self.api.parse_feeds(feeds_json)

    def after_update(self) -> None:
        self.logger.info('Running after update command: %s' %
                         ' '.join(self.api.after_cleanup_command))
        self.cli.run(self.api.after_cleanup_command)


class CliUpdaterV15(CliUpdater):
    """Cli Updater for Nextcloud News v15+"""

    def start_update_thread(self, feeds: List[Feed]) -> CliUpdateThread:
        return CliUpdateThreadV15(feeds, self.logger, self.api, self.cli)

    def all_feeds(self) -> List[Feed]:
        self.logger.info('Running get user list command: %s' %
                         ' '.join(self.api.users_list_command))
        users_json = self.cli.run(self.api.users_list_command).strip()
        users_json = str(users_json, 'utf-8')
        users = self.api.parse_users(users_json)

        feeds_list = []
        for userID in users:
            self.logger.info('Running get feeds for user "%s" command: %s' %
                             (userID, ' '.join(self.api.all_feeds_command)))
            cmd = self.api.all_feeds_command + [userID]
            feeds_json_bytes = self.cli.run(cmd).strip()
            feeds_json = str(feeds_json_bytes, 'utf-8')
            self.logger.info('Received these feeds to update for user %s: %s' %
                             (userID, feeds_json))
            feeds_list += self.api.parse_feeds(feeds_json, userID)

        return feeds_list
