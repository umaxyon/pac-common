# coding:utf-8
import os
from bson.codec_options import CodecOptions
from tzlocal import get_localzone
from pymongo import MongoClient
from pymongo.collection import Collection

from common.const import MONGO_DB_HOST
from common.const import MONGO_DB_NAME
from common.const import MONGO_DB_PORT
from common.log import Log


class DB(object):

    def __init__(self, path=None):
        if not path:
            if os.name == 'nt':
                path = 'mongodb://{}:{}'.format(MONGO_DB_HOST, MONGO_DB_PORT)
            else:
                path = 'mongodb://%s:%s@%s:%s/%s' % (
                    'pacPac', 'Npa98ksA', MONGO_DB_HOST, MONGO_DB_PORT, MONGO_DB_NAME)

        Log.debug("dbpath = {}".format(path))
        self.client = MongoClient(path)


class Dao(object):
    def __init__(self, db):
        self._db = db

    def table(self, col_name, dbname='dbpacpac') -> Collection:
        return self._db.client.get_database(dbname, CodecOptions(tz_aware=True, tzinfo=get_localzone()))[col_name]
