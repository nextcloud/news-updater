#!/usr/bin/env python3
"""
Updater script for the news app which allows multiple feeds to be updated at
once to speed up the update process. Built in cron has to be disabled in the
news config, see the README.rst file in the top directory for more information.
"""
import argparse
import sys
from platform import python_version

from owncloud_news_updater.config import ConfigParser, Config, merge_configs, \
    ConfigValidator
from owncloud_news_updater.updaters.cli import CliUpdater, create_cli_api
from owncloud_news_updater.updaters.web import WebUpdater, create_web_api
from owncloud_news_updater.version import get_version

__author__ = 'Bernhard Posselt'
__copyright__ = 'Copyright 2012-2016, Bernhard Posselt'
__license__ = 'GPL3+'
__maintainer__ = 'Bernhard Posselt'
__email__ = 'dev@bernhard-posselt.com'


def main():
    if sys.version_info < (3, 2):
        print('Error: Python 3.2 required but found %s' % python_version())
        exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', '-t',
                        help='How many feeds should be fetched in parallel, '
                             'defaults to 10',
                        type=int)
    parser.add_argument('--timeout', '-s',
                        help='Maximum number of seconds for updating a feed, \
              defaults to 5 minutes',
                        type=int)
    parser.add_argument('--interval', '-i',
                        help='Update interval between fetching the next '
                             'round of updates in seconds, defaults to 15 '
                             'minutes. The update timespan will be '
                             'subtracted from the interval.',
                        type=int)
    parser.add_argument('--apilevel', '-a',
                        help='API level. Use v2 for News 9.0.0 or greater, '
                             'v1-2 for lower versions',
                        choices=['v1-2', 'v2'])
    parser.add_argument('--loglevel', '-l',
                        help='Log granularity, info will log all urls and '
                             'received data, error will only log errors',
                        choices=['info', 'error'])
    parser.add_argument('--config', '-c',
                        help='Path to config file where all parameters '
                             'except can be defined as key values pair. An '
                             'example is in bin/example_config.ini')
    parser.add_argument('--phpini', '-P',
                        help='Custom absolute path to the php.ini file to use '
                             'for the command line updater. If omitted, the '
                             'default one will be used')
    parser.add_argument('--user', '-u',
                        help='Admin username to log into ownCloud. Must be '
                             'specified on the command line or in the config '
                             'file if the updater should update over HTTP')
    parser.add_argument('--password', '-p',
                        help='Admin password to log into ownCloud if the '
                             'updater should update over HTTP')
    parser.add_argument('--version', '-v', action='version',
                        version=get_version(),
                        help='Prints the updater\'s version')
    parser.add_argument('--mode', '-m',
                        help='Mode to run the updater in: endless runs the '
                             'update again after the specified interval, '
                             'singlerun only executes the update once',
                        choices=['endless', 'singlerun'])
    parser.add_argument('url',
                        help='The URL or absolute path to the directory '
                             'where owncloud is installed. Must be specified '
                             'on the command line or in the config file. If '
                             'the URL starts with http:// or https://, '
                             'a user and password are required. Otherwise the '
                             'updater tries to use the console based API '
                             'which was added in 8.1.0',
                        nargs='?')
    args = parser.parse_args()

    # read config file if given
    if args.config:
        config_parser = ConfigParser()
        config = config_parser.parse_file(args.config)
    else:
        config = Config()

    merge_configs(args, config)

    validator = ConfigValidator()
    validation_result = validator.validate(config)
    if len(validation_result) > 0:
        for message in validation_result:
            print('Error: %s' % message, file=sys.stderr)
        print()
        parser.print_help(sys.stderr)
        exit(1)

    # create the updater and run the threads
    if config.is_web():
        api = create_web_api(config.apilevel, config.url)
        updater = WebUpdater(config, api)
    else:
        api = create_cli_api(config.apilevel, config.url, config.phpini)
        updater = CliUpdater(config, api)
    updater.run()


if __name__ == '__main__':
    main()
