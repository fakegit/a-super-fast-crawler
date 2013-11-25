#coding:utf8
import logging
import os

SPIDER_ROOT = os.path.dirname(os.path.realpath(__file__))


class LogManager(object):
    def __init__(self, logFile="", logLevel=0, logTree=""):
        logFile = SPIDER_ROOT+"/log/"+ logFile
        try:
            self.logger = self.configLogger(logFile=logFile, logLevel=logLevel, logTree=logTree)
        except:
            #todo
            raise Exception, "log init error"

    def configLogger(self, logFile="", logLevel=0, logTree=""):
        '''配置logging的日志文件以及日志的记录等级'''
        logger = logging.getLogger(logTree)
        LEVELS = {
            1: logging.CRITICAL,
            2: logging.ERROR,
            3: logging.WARNING,
            4: logging.INFO,
            5: logging.DEBUG,  # 数字最大记录最详细
        }
        formatter = logging.Formatter(
            '%(asctime)s %(threadName)s %(levelname)s %(message)s')
        try:
            fileHandler = logging.FileHandler(logFile)
        except IOError, e:
            raise IOError
        else:
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
            logger.setLevel(LEVELS.get(logLevel))
            return logger
