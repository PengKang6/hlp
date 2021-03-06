import os
import logging
import tensorflow as tf
from optparse import OptionParser


class CmdParser(OptionParser):
    def error(self, msg):
        print('Error!提示信息如下：')
        self.print_help()
        self.exit(0)

    def exit(self, status=0, msg=None):
        exit(status)


def log_operator(level: str, log_file: str = None,
                 log_format: str = "[%(levelname)s] - [%(asctime)s] - [file: %(filename)s] - "
                                   "[function: %(funcName)s] - [%(message)s]") -> logging.Logger:
    """
    日志操作方法，日志级别有'CRITICAL','FATAL','ERROR','WARN','WARNING','INFO','DEBUG','NOTSET'
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    Args:
        log_file: 日志路径
        message: 日志信息
        level: 日志级别
        log_format: 日志信息格式
    Returns:
    """
    if log_file is None:
        log_file = os.path.dirname(__file__)[:-6] + 'data\\runtime.log'

    logger = logging.getLogger()
    logger.setLevel(level)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level=level)
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
