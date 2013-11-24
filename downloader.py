#!/usr/bin/env python
# encoding: utf-8
import os
import threading
import urllib2

class Downloader(threading.Thread):
    """Threaded File Downloader"""

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # gets the url from the queue
            url = self.queue.get()

            # download the file
            self.download_file(url)

            # send a signal to the queue that the job is done
            self.queue.task_done()

    def download_file(self, url):
        """"""
        headers = {
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset' : 'gb18030,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding' : 'gzip,deflate,sdch',
            'Accept-Language' : 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Trident/5.0)',
            'Referer' : url,
        }

        req = urllib2.Request(url, None, headers)
        resp = urllib2.urlopen(req)

        fname = os.path.basename(url)
        with open(fname, "wb") as f:
            while True:
                chunk = resp.read(1024)
                if not chunk: break
                f.write(chunk)
