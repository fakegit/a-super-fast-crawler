#!/usr/bin/env python
#encoding:utf-8
"""
spider-scheduler.py
"""
import datetime
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/crawler/'

sys.path.insert(0, PROJECT_ROOT)

import scheduler
from crawler import application

#set our spider task here.
#TODO may crontab better?
spider_task = scheduler.Task("spider",
                             datetime.datetime.now(),
                             scheduler.daily_at(datetime.time(0, 0)),
                             scheduler.RunUntilSuccess(application.main, num_tries=5))

#set up scheduler to distribute tasks
spider_scheduler = scheduler.Scheduler()

spider_id = spider_scheduler.schedule_task(spider_task)

spider_scheduler.start()

# Give it a timeout to halt any running tasks and stop gracefully
spider_scheduler.join()
