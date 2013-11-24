#!/usr/bin/env python
# encoding: utf-8
# """
# database.py
# ~~~~~~~~~~~~~

# 该模块提供爬虫所需的mongo数据库的创建、连接、断开，以及数据的存储功能。
# """

from pymongo import Connection
from pymongo.errors import ConnectionFailure
from config import MONGO_SETTINGS

class Database(object):
    def __init__(self, host=MONGO_SETTINGS["host"], port=MONGO_SETTINGS["port"], db=MONGO_SETTINGS["database"]):
        try:
            self.conn = Connection(host=host, port=port)
            self.db = self.conn[db]
        except ConnectionFailure, e:
            log.error("connection error")
            self.conn = None

    def isConn(self):
        if self.conn:
            return True
        else:
            return False

    def saveData(self, collection='', query={}, document=''):
        if self.db[collection].find_one(query):
            self.db[collection].update(query, {"$set": document})
        else:
            document['_id'] = self.get_id(collection=collection)
            self.db[collection].save(document, safe=True)

    def getAllData(self, collection=''):
        if self.conn and collection:
            return self.db[collection].find()
        else:
            return []

    def close(self):
        if self.conn:
            self.conn.close()
        else:
            pass

    def saveMedia(self, ):
        pass

    def get_last_insert_id(self, collection=''):
        self.db[collection].find().sort({"_id":1}).limit(1)[0]['_id']

    def get_id(self, collection=None):
        value = self.db["ids"].find_and_modify(
            {"name": collection}, {"$inc": {"value": 1}}, new=True, upsert=True)
        return value["value"]
