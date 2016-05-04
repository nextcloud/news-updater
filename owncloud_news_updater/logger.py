import logging


class Logger:
    def __init__(self, config):
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=log_format)
        self.logger = logging.getLogger('ownCloud News Updater')
        if config.loglevel == 'info':
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.ERROR)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)
