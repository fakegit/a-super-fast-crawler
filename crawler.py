#!/usr/bin/env python
# encoding: utf-8
"""
crawler.py
~~~~~~~~~~~~~

主要模块，爬虫的具体实现。
"""
import re
import time
import logging
import threading
import traceback
from hashlib import md5
from bs4 import BeautifulSoup
from datetime import datetime
from collections import deque
from locale import getdefaultlocale
from urlparse import urljoin,urlparse

from database import Database
from webPage import WebPage
from threadPool import ThreadPool

log = logging.getLogger('spider')


class Crawler(threading.Thread):

    def __init__(self, args, queue):
        threading.Thread.__init__(self)
        #指定网页深度
        self.depth = args['depth']
        #标注初始爬虫深度，从1开始
        self.currentDepth = 1
        #指定关键词,使用console的默认编码来解码
        self.keyword = args['keyword'].decode(getdefaultlocale()[1])
        #数据库
        self.database =  Database(db="bt_tornado")
        #线程池,指定线程数
        self.threadPool = ThreadPool(args['threadNum'])
        #已访问的链接
        self.visitedHrefs = set()
        #待访问的链接
        self.unvisitedHrefs = deque()
        #添加待访问的链接
        for url in args['url']:
            self.unvisitedHrefs.append(url)
        #标记爬虫是否开始执行任务
        self.isCrawling = False
        # allow or deny crawl url
        self.entryFilter = args['entryFilter']
        # allow to output back url
        self.yieldFilter = args['yieldFilter']
        #
        self.callbackFilter = args['callbackFilter']
        #
        self.db = args['db']
        self.collection = args['collection']
        # communication queue
        self.queue = queue

    def run(self):
        print '\nStart Crawling\n'
        if not self._isDatabaseAvaliable():
            print 'Error: Unable to open database file.\n'
        else:
            self.isCrawling = True
            self.threadPool.startThreads()
            while self.currentDepth < self.depth+1:
                #分配任务,线程池并发下载当前深度的所有页面（该操作不阻塞）
                self._assignCurrentDepthTasks ()
                #等待当前线程池完成所有任务,当池内的所有任务完成时，即代表爬完了一个网页深度
                #self.threadPool.taskJoin()可代替以下操作，可无法Ctrl-C Interupt
                while self.threadPool.getTaskLeft():
                    time.sleep(8)
                print 'Depth %d Finish. Totally visited %d links. \n' % (
                    self.currentDepth, len(self.visitedHrefs))
                log.info('Depth %d Finish. Total visited Links: %d\n' % (
                    self.currentDepth, len(self.visitedHrefs)))
                self.currentDepth += 1
            self.stop()

    def stop(self):
        self.isCrawling = False
        self.threadPool.stopThreads()
        self.database.close()
        #use queue to communicate between threads
        self.queue.get()
        self.queue.task_done()

    def getAlreadyVisitedNum(self):
        #visitedHrefs保存已经分配给taskQueue的链接，有可能链接还在处理中。
        #因此真实的已访问链接数为visitedHrefs数减去待访问的链接数
        return len(self.visitedHrefs) - self.threadPool.getTaskLeft()

    def _assignCurrentDepthTasks(self):
        while self.unvisitedHrefs:
            url = self.unvisitedHrefs.popleft()
            if not self.__entry_filter(url):
                self.visitedHrefs.add(url)
                continue
            #向任务队列分配任务
            self.threadPool.putTask(self._taskHandler, url)
            #标注该链接已被访问,或即将被访问,防止重复访问相同链接
            self.visitedHrefs.add(url)

    def _callback_filter(self, webPage):
        #parse the web page to do sth
        url , pageSource = webPage.getDatas()
        for tmp  in self.callbackFilter['List']:
            if re.compile(tmp,re.I|re.U).search(url):
                self.callbackFilter['func'](webPage)

    def _taskHandler(self, url):
        #先拿网页源码，再保存,两个都是高阻塞的操作，交给线程处理
        webPage = WebPage(url)
        tmp = webPage.fetch()
        if tmp:
            self._callback_filter(webPage)
            self._saveTaskResults(webPage)
            self._addUnvisitedHrefs(webPage)

    def _saveTaskResults(self, webPage):
        url, pageSource = webPage.getDatas()
        _id = md5(url).hexdigest()
        try:
            if self.__yield_filter(url):
                query = {"id": _id}
                document = {"id": _id, "url":url, "createTime": datetime.now()}
                self.database.saveData(query=query, collection=self.collection, document=document)
        except Exception, e:
            log.error(' URL: %s ' % url + traceback.format_exc())

    def _addUnvisitedHrefs(self, webPage):
        '''添加未访问的链接。将有效的url放进UnvisitedHrefs列表'''
        #对链接进行过滤:1.只获取http或https网页;2.保证每个链接只访问一次
        url, pageSource = webPage.getDatas()
        hrefs = self._getAllHrefsFromPage(url, pageSource)
        for href in hrefs:
            if self._isHttpOrHttpsProtocol(href):
                if not self._isHrefRepeated(href):
                    self.unvisitedHrefs.append(href)

    def _getAllHrefsFromPage(self, url, pageSource):
        '''解析html源码，获取页面所有链接。返回链接列表'''
        hrefs = []
        soup = BeautifulSoup(pageSource)
        results = soup.find_all('a',href=True)
        for a in results:
            #必须将链接encode为utf8, 因为中文文件链接如 http://aa.com/文件.pdf
            #在bs4中不会被自动url编码，从而导致encodeException
            href = a.get('href').encode('utf8')
            if not href.startswith('http'):
                href = urljoin(url, href)#处理相对链接的问题
            hrefs.append(href)
        return hrefs

    def _isHttpOrHttpsProtocol(self, href):
        protocal = urlparse(href).scheme
        if protocal == 'http' or protocal == 'https':
            return True
        return False

    def _isHrefRepeated(self, href):
        if href in self.visitedHrefs or href in self.unvisitedHrefs:
            return True
        return False

    def _isDatabaseAvaliable(self):
        if self.database.isConn():
            return True
        return False

    def __entry_filter(self, checkURL):
        '''
        入口过滤器
        决定了爬虫可以进入哪些url指向的页面进行抓取

        @param checkURL: 交给过滤器检查的url
        @type checkURL: 字符串

        @return: 通过检查则返回True，否则返回False
        @rtype: 布尔值
        '''
        # 如果定义了过滤器则检查过滤器
        if self.entryFilter:
            if self.entryFilter['Type'] == 'allow':        # 允许模式，只要满足一个就允许，否则不允许
                result = False
                for rule in self.entryFilter['List']:
                    pattern = re.compile(rule, re.I | re.U)
                    if pattern.search(checkURL):
                        result = True
                        break
                return result
            elif self.entryFilter['Type'] == 'deny':        # 排除模式，只要满足一个就不允许，否则允许
                result = True
                for rule in self.entryFilter['List']:
                    pattern = re.compile(rule, re.I | re.U)
                    if pattern.search(checkURL):
                        result = False
                        break
                return result

        # 没有过滤器则默认允许
        return True

    def __yield_filter(self, checkURL):
        '''
        生成过滤器
        决定了爬虫可以返回哪些url

        @param checkURL: 交给过滤器检查的url
        @type checkURL: 字符串

        @return: 通过检查则返回True，否则返回False
        @rtype: 布尔值
        '''
        # 如果定义了过滤器则检查过滤器
        if self.yieldFilter:
            if self.yieldFilter['Type'] == 'allow':        # 允许模式，只要满足一个就允许，否则不允许
                result = False
                for rule in self.yieldFilter['List']:
                    pattern = re.compile(rule, re.I | re.U)
                    if pattern.search(checkURL):
                        result = True
                        break
                return result
            elif self.yieldFilter['Type'] == 'deny':        # 排除模式，只要满足一个就不允许，否则允许
                result = True
                for rule in self.yieldFilter['List']:
                    pattern = re.compile(rule, re.I | re.U)
                    if pattern.search(checkURL):
                        result = False
                        break
                return result

        # 没有过滤器则默认允许
        return True
