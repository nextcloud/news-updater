#!/usr/bin/env python3
"""
Updater script for the news app which allows multiple feeds to be updated at
once to speed up the update process. Built in cron has to be disabled in the
news config, see the README.rst file in the top directory for more information.
"""
import argparse
import configparser
import os
import sys
from platform import python_version

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
    parser.add_argument('--testrun',
                        help='Run update only once, DO NOT use this in a '
                             'cron job, only recommended for testing',
                        action='store_true')
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
        config = configparser.ConfigParser()
        files = config.read(args.config)

        if len(files) <= 0:
            print('Error: could not find config file %s' % args.config)
            exit(1)

        ini_values = config['updater']

        # parse using proper data types
        def to_str(section, key):
            return section.get(key)

        def to_int(section, key):
            return int(section.get(key))

        def to_bool(section, key):
            return int(section.getboolean(key))

        valid_ini_values = {
            'user': to_str,
            'password': to_str,
            'threads': to_int,
            'interval': to_int,
            'url': to_str,
            'loglevel': to_str,
            'phpini': to_str,
            'apilevel': to_str
        }
        for ini_key, getter in valid_ini_values.items():
            if use_ini_param(args, ini_values, ini_key):
                setattr(args, ini_key, getter(ini_values, ini_key))
    if not args.url:
        _exit(parser, 'No url or directory given')

    # if url starts with a /, the console based API will be used
    isWeb = args.url.startswith('http://') or args.url.startswith('https://')

    # url and user must be specified either from the command line or in the
    # config file
    if isWeb and not args.user:
        _exit(parser, 'Web API requires a user')

    if not isWeb and not os.path.isabs(args.url):
        _exit(parser,
              ('Absolute path to ownCloud installation required, given '
               '%s') % args.url)

    if not isWeb and not os.path.isdir(args.url):
        _exit(parser, '%s is not a directory' % args.url)

    # fill args with defaults, necessary because there is no proper way to find
    # out if it should be overwritten by a config setting
    defaults = {
        'loglevel': 'error',
        'interval': 15 * 60,
        'timeout': 5 * 60,
        'apilevel': 'v1-2',
        'threads': 10
    }

    for key, default in defaults.items():
        if not getattr(args, key):
            setattr(args, key, default)

    # create the updater and run the threads
    if isWeb:
        api = create_web_api(args.apilevel, args.url)
        updater = WebUpdater(args.threads, args.interval, args.testrun,
                             args.loglevel, args.timeout, api, args.user,
                             args.password)
    else:
        api = create_cli_api(args.apilevel, args.url, args.phpini)
        updater = CliUpdater(args.threads, args.interval, args.testrun,
                             args.loglevel, api)
    updater.run()


def use_ini_param(args, ini_values, ini_key):
    return not getattr(args, ini_key) and ini_key in ini_values


def _exit(parser, message):
    print(message, file=sys.stderr)
    parser.print_help()
    exit(1)


if __name__ == '__main__':
    main()
