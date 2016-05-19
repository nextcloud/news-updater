#!/usr/bin/env python3
"""
Updater script for the news app which allows multiple feeds to be updated at
once to speed up the update process. Built in cron has to be disabled in the
news config, see the README.rst file in the top directory for more information.
"""
import sys
from platform import python_version

from nextcloud_news_updater.container import Container
from nextcloud_news_updater.api.updater import Updater

__author__ = 'Bernhard Posselt'
__copyright__ = 'Copyright 2012-2016, Bernhard Posselt'
__license__ = 'GPL3+'
__maintainer__ = 'Bernhard Posselt'
__email__ = 'dev@bernhard-posselt.com'

if sys.version_info < (3, 4):
    print('Error: Python 3.4 required but found %s' % python_version())
    exit(1)


def main() -> None:
    container = Container()
    container.resolve(Updater).run()


if __name__ == '__main__':
    main()
