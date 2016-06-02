import argparse
from typing import Any

from nextcloud_news_updater.version import get_version


class ArgumentParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--threads', '-t',
                                 help='How many feeds should be fetched in '
                                      'parallel, defaults to 10',
                                 type=int)
        self.parser.add_argument('--timeout', '-s',
                                 help='Maximum number of seconds for updating '
                                      'a feed, defaults to 5 minutes',
                                 type=int)
        self.parser.add_argument('--interval', '-i',
                                 help='Update interval between fetching the '
                                      'next round of updates in seconds, '
                                      'defaults to 15 minutes. The update '
                                      'timespan will be subtracted from the '
                                      'interval.',
                                 type=int)
        self.parser.add_argument('--apilevel', '-a',
                                 help='API level. Use v2 for News 9.0.0 or '
                                      'greater, v1-2 for lower versions',
                                 choices=['v1-2', 'v2'])
        self.parser.add_argument('--loglevel', '-l',
                                 help='Log granularity, info will log all '
                                      'urls and received data, error will '
                                      'only log errors',
                                 choices=['info', 'error'])
        self.parser.add_argument('--config', '-c',
                                 help='Path to config file where all '
                                      'parameters except can be defined as '
                                      'key values pair. An example is in '
                                      'bin/example_config.ini')
        self.parser.add_argument('--phpini', '-P',
                                 help='Custom absolute path to the php.ini '
                                      'file to use for the command line '
                                      'updater. If omitted, the default one '
                                      'will be used')
        self.parser.add_argument('--user', '-u',
                                 help='Admin username to log into Nextcloud. '
                                      'Must be specified on the command line '
                                      'or in the config file if the updater '
                                      'should update over HTTP')
        self.parser.add_argument('--password', '-p',
                                 help='Admin password to log into Nextcloud '
                                      'if the updater should update over HTTP'
                                 )
        self.parser.add_argument('--version', '-v', action='version',
                                 version=get_version(),
                                 help='Prints the updater\'s version')
        self.parser.add_argument('--mode', '-m',
                                 help='Mode to run the updater in: endless '
                                      'runs the update again after the '
                                      'specified interval, singlerun only '
                                      'executes the update once',
                                 choices=['endless', 'singlerun'])
        self.parser.add_argument('url',
                                 help='The URL or absolute path to the '
                                      'directory where Nextcloud is installed.'
                                      ' Must be specified on the command line '
                                      'or in the config file. If the URL '
                                      'starts with http:// or https://, a '
                                      'user and password are required. '
                                      'Otherwise the updater tries to use the '
                                      'console based API which was added in '
                                      '8.1.0',
                                 nargs='?')

    def parse(self) -> Any:
        return self.parser.parse_args()

    def print_help(self, file: Any) -> None:
        self.parser.print_help(file)
