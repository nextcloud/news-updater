import logging

from nextcloud_news_updater.config import Config


class Logger:
    def __init__(self, config: Config) -> None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=log_format)
        self.logger = logging.getLogger('Nextcloud News Updater')
        if config.loglevel == 'info':
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.ERROR)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)
