# -- coding: utf-8 --
import logging
import os

loggers = {}  # 全局字典，用于存储已创建的日志记录器

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.dirname(dir_path)


class LoggerSports:

    def __init__(self, ball, api, level='DEBUG'):

        log_name = f'{ball}_{api}'
        formatter_str = f'%(asctime)s [{ball}_{api}] %(levelname)s: %(message)s'

        if log_name in loggers:
            # 如果已存在相应名称的日志记录器，则直接使用现有的日志记录器
            self.logger = loggers[log_name]
        else:

            # log_file = f'{dir_path}/log/{log_name}.log'

            self.logger = logging.getLogger(log_name)
            self.logger.setLevel(level)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # file_handler = logging.FileHandler(log_file, encoding='UTF-8')
            # file_handler.setLevel(level)

            formatter = logging.Formatter(formatter_str)
            console_handler.setFormatter(formatter)
            # file_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)
            # self.logger.addHandler(file_handler)

            # 将新创建的日志记录器存储到全局字典中
            loggers[log_name] = self.logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


if __name__ == '__main__':
    log = LoggerSports(ball='football', api='fb')
    log.debug('debug')
    log.info('info')
    log.warning('警告')
    log.error('报错')
    log.critical('严重')

