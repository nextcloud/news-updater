import sys

from owncloud_news_updater.argumentparser import ArgumentParser
from owncloud_news_updater.config import ConfigParser, ConfigValidator, \
    Config, \
    merge_configs
from owncloud_news_updater.dependencyinjection.container import BaseContainer
from owncloud_news_updater.logger import Logger
from owncloud_news_updater.updaters.cli import CliUpdater, Cli, CliApi, \
    create_cli_api
from owncloud_news_updater.updaters.updater import Updater
from owncloud_news_updater.updaters.web import create_web_api, WebApi, \
    WebUpdater, HttpClient


class Container(BaseContainer):
    def __init__(self):
        super().__init__()
        self.set(ArgumentParser, lambda c: ArgumentParser())
        self.set(Config, lambda c: self._create_config(c))
        self.set(ConfigParser, lambda c: ConfigParser())
        self.set(ConfigValidator, lambda c: ConfigValidator())
        self.set(Logger, lambda c: Logger(c.get(Config)))
        self.set(Cli, lambda c: Cli())
        self.set(HttpClient, lambda c: HttpClient())
        self.set(CliUpdater, lambda c: CliUpdater(c.get(Config), c.get(Logger),
                                                  c.get(CliApi), c.get(Cli)))
        self.set(WebUpdater, lambda c: WebUpdater(c.get(Config), c.get(Logger),
                                                  c.get(WebApi),
                                                  c.get(HttpClient)))
        self.set(CliApi, lambda c: create_cli_api(c.get(Config)))
        self.set(WebApi, lambda c: create_web_api(c.get(Config)))
        self.set(Updater, lambda c: self._create_updater(c))

    def _create_updater(self, container):
        if container.get(Config).is_web():
            return container.get(WebUpdater)
        else:
            return container.get(CliUpdater)

    def _create_config(self, container):
        parser = container.get(ArgumentParser)
        args = parser.parse()
        if args.config:
            config_parser = container.get(ConfigParser)
            config = config_parser.parse_file(args.config)
        else:
            config = Config()

        merge_configs(args, config)

        validator = container.get(ConfigValidator)

        validation_result = validator.validate(config)
        if len(validation_result) > 0:
            for message in validation_result:
                print('Error: %s' % message, file=sys.stderr)
            print()
            parser.print_help(sys.stderr)
            exit(1)

        return config
