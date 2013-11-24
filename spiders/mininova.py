#!/usr/bin/env python
# encoding: utf-8
import re
from bs4 import BeautifulSoup
from hashlib import md5

from database import Database
from config import MONGO_SETTINGS

# Spider Factory
def spider():
    def callback(webPage):
        url, pageSource = webPage.getDatas()
        soup = BeautifulSoup(pageSource)
        #tmp var
        _ = ''
        #more robust
        param = {}
        #calculate id to avoid repeat data
        param['id'] = md5(url).hexdigest(),
        #get url
        param['url'] = url,
        #get name
        try:
            _ = soup.find(id="content").h1.string
        except:
            _ = 'unknown'
        finally:
            param['name'] = _
        #get size
        try:
            _ = soup.find(
                id='specifications'
                ).find_all("p")[2].get_text().strip().split('\n')[1].replace(u'\xa0', u' '),
        except:
            _ = 'unknown'
        finally:
            param['size'] = _
        #get description
        try:
            _ = re.compile(r'[\n\r\t]').sub(
                " ",soup.find(id='description').get_text()),
        except:
            _ = 'not description right now~XD'
        finally:
            param['description'] = _
        #get magnet_link
        try:
            _ = soup.find(id="download").find_all("a")[2]['href']
        except:
            #drop it or redo?
            return
        else:
            param['magnet_link'] = _
        query = {"id": param['id']}
        database = Database(db=MONGO_SETTINGS.database)
        database.saveData(collection='seed', query=query, document=param)

    #args to init spider
    entryFilter = dict()
    entryFilter['Type'] = 'allow'
    entryFilter['List'] = [r'/tor/\d+', r'/today', r'/yesterday', r'/sub/\d+']

    yieldFilter = dict()
    # yieldFilter['Type'] = 'allow'
    # yieldFilter['List'] = [r'$']
    callbackFilter = dict()
    callbackFilter['List'] = [r'/tor/\d+', ]
    callbackFilter['func'] = callback

    args = dict(
        url=['http://www.mininova.org/today', 'http://www.mininova.org/yesterday'],
        depth=3,
        threadNum=4,
        keyword='',
        entryFilter=entryFilter,
        yieldFilter=yieldFilter,
        callbackFilter=callbackFilter,
        db='bt_tornado',
        collection='link2search',
    )

    return args
