#coding:utf8
"""
yet another logging wrapper

- log level
   logging.CRITICAL,
   logging.ERROR,
   logging.WARNING,
   logging.INFO,
   logging.DEBUG
"""
import logging

from config import PROJECT_ROOT

def configLogger(logFile="spider.log", logLevel=logging.DEBUG, logTree=""):
    logFile = PROJECT_ROOT+"/log/"+ logFile
    '''配置logging的日志文件以及日志的记录等级'''
    logger = logging.getLogger(logTree)
    formatter = logging.Formatter(
        '%(asctime)s %(threadName)s %(levelname)s %(message)s')
    try:
        fileHandler = logging.FileHandler(logFile)
    except IOError, e:
        raise IOError
    else:
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.setLevel(logLevel)
        return logger
