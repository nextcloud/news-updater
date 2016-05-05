import sys

from owncloud_news_updater.api.cli import CliUpdater, CliApi, \
    create_cli_api
from owncloud_news_updater.api.updater import Updater
from owncloud_news_updater.api.web import create_web_api, WebApi, \
    WebUpdater
from owncloud_news_updater.common.argumentparser import ArgumentParser
from owncloud_news_updater.config import ConfigParser, ConfigValidator, \
    Config, merge_configs
from owncloud_news_updater.dependencyinjection.container import \
    Container as BaseContainer


class Container(BaseContainer):
    def __init__(self):
        super().__init__()
        self.register(CliApi, lambda c: create_cli_api(c.resolve(Config)))
        self.register(WebApi, lambda c: create_web_api(c.resolve(Config)))
        self.register(Updater, self._create_updater)
        self.register(Config, self._create_config)

    def _create_updater(self, container):
        if container.resolve(Config).is_web():
            return container.resolve(WebUpdater)
        else:
            return container.resolve(CliUpdater)

    def _create_config(self, container):
        parser = container.resolve(ArgumentParser)
        args = parser.parse()
        if args.config:
            config_parser = container.resolve(ConfigParser)
            config = config_parser.parse_file(args.config)
        else:
            config = Config()

        merge_configs(args, config)

        validator = container.resolve(ConfigValidator)

        validation_result = validator.validate(config)
        if len(validation_result) > 0:
            for message in validation_result:
                print('Error: %s' % message, file=sys.stderr)
            print()
            parser.print_help(sys.stderr)
            exit(1)

        return config
