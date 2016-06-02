import configparser
import os
from typing import List, Union, Any
from typing import Optional


class InvalidConfigException(Exception):
    pass


class InvalidConfigKeyException(Exception):
    pass


class Types:
    """
    In Python 3.4 we could use enums
    """
    integer = 0
    boolean = 1
    string = 2


class Config:
    """
    Class that holds the config values, defaults etc
    Once 3.5 can be required, we can add typings :D
    """
    config_keys = {
        'user': Types.string,
        'password': Types.string,
        'url': Types.string,
        'loglevel': Types.string,
        'phpini': Types.string,
        'apilevel': Types.string,
        'mode': Types.string,
        'threads': Types.integer,
        'interval': Types.integer,
    }

    def __init__(self) -> None:
        self.loglevel = 'error'
        self.interval = 15 * 60
        self.timeout = 5 * 60
        self.apilevel = 'v1-2'
        self.threads = 10
        self.mode = 'endless'
        self.password = ''
        self.user = None  # type: Optional[str]
        self.url = None  # type: Optional[str]
        self.phpini = None  # type: Optional[str]

    def is_web(self) -> bool:
        return self.url is not None and (self.url.startswith('http://') or
                                         self.url.startswith('https://'))


class ConfigValidator:
    def validate(self, config: Config) -> List[str]:
        result = []  # type: List[str]
        if not config.url:
            return ['No url given']

        if config.is_web() and not config.user:
            return ['Url given but no user present']
        elif not config.is_web() and not os.path.isabs(config.url):
            return ['Absolute path or full Url required']
        elif not config.is_web() and not os.path.isdir(config.url):
            return ['Given path is not a directory']

        if config.mode not in ['endless', 'singlerun']:
            result += ['Unknown mode: %s' % config.mode]
        if config.loglevel not in ['info', 'error']:
            result += ['Unknown loglevel: %s' % config.loglevel]
        if config.apilevel not in ['v1-2', 'v2']:
            result += ['Unknown apilevel: %s' % config.apilevel]

        if config.phpini and not os.path.isabs(config.phpini):
            result += ['Path to php.ini must be absolute']

        return result


class ConfigParser:
    def parse_file(self, path: str) -> Config:
        parser = configparser.ConfigParser()
        successfully_parsed = parser.read(path)
        if len(successfully_parsed) <= 0:
            raise InvalidConfigException(
                'Error: could not find config file %s' % path)
        contents = parser['updater']

        config = Config()
        for key in contents:
            if not hasattr(config, key):
                msg = 'Error: unknown config key with name "%s"' % key
                raise InvalidConfigKeyException(msg)

        for key, type_enum in Config.config_keys.items():
            if key in contents:
                value = self._parse_ini_value(type_enum, contents, key)
                setattr(config, key, value)

        return config

    def _parse_ini_value(self, type_enum: int, contents: Any, key: str) -> \
            Union[str, int, bool]:
        if type_enum == Types.integer:
            return int(contents.get(key))
        elif type_enum == Types.boolean:
            return contents.getboolean(key)
        else:
            return contents.get(key)


def merge_configs(args: Any, config: Config) -> None:
    """
    Merges values from argparse and configparser. Values from argparse will
    always override values from the config. Resulting values are set on the
    config object
    :argument args the argument parser arguments
    :argument config the config
    """
    for key, type_enum in Config.config_keys.items():
        if hasattr(args, key) and getattr(args, key):
            setattr(config, key, getattr(args, key))
