#!/usr/bin/env python
# encoding: utf-8
import traceback
from datetime import datetime
from Queue import Queue

import util
from crawler import Crawler
from database import Database
from logmanager import LogManager
from spiders import mininova
from config import CURRENT_DIR, MONGO_SETTINGS
from monitor import send_mail

class SpiderManager(object):
    def __init__(self, spiders=None, db=None):
        try:
            self.logger = LogManager(
                logFile='spider.log', logLevel=5, logTree="spider").logger
        except:
            #TODO format the backtrace
            raise Exception, "can not init logger"
        self.queue = Queue()
        self.database = Database(db=db)
        self.spiders = spiders

    def run(self):

        self.logger.info("the spider has been running!")

        #create a global thread num
        for num in range(len(self.spiders)):
            self.queue.put(num)
        try:
            for spider in self.spiders:
                crawler = Crawler(spider, self.queue)
                crawler.start()
            self.queue.join()
        except:
            self.logger.error("spider cannot run.")
        finally:
            seed_num = self.database.db['seed'].count()
            textfile = CURRENT_DIR + '/log/spider.log'
            self.logger.info("now your seeds num is %s." % seed_num)
            try:
                fp = open(textfile, 'rb')
                content = util.tail(fp)
                fp.close()
                sub = 'bt-share-log-%s' % datetime.now()
                send_mail(['zhkzyth@gmail.com', ], sub, content)
            except:
                self.logger.error(traceback.format_exc())


def main():
    """
       test case for our spider
    """
    spiders = [mininova.spider(), ]
    crawler = SpiderManager(spiders, MONGO_SETTINGS["database"])
    crawler.run()

if __name__ == "__main__":
    main()
