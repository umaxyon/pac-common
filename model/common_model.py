# coding:utf-8
from attrdict import AttrDict
from common.dao import Dao


class CommonModel(object):

    def __init__(self, dao: Dao):
        self.dao = dao

    def find_stock_report_by_ccode(self, ccode):
        cur = self.dao.table('stock_report_pre').find_one({'ccode': ccode})
        return {} if cur is None else AttrDict(dict(cur))

    def find_tweet_by_id(self, id_str):
        """tweetをidで検索する"""
        cur = self.dao.table('tweet').find({'id_str': id_str})
        tweet = [r for r in cur]
        return {} if not tweet else AttrDict(tweet[0])

    def find_last_price_history(self, ccode):
        """最後の終値(多くの場合前日)を取得する"""
        cur_history = self.dao.table(ccode, dbname='price_history').find({}).sort(
            [('date', -1)]).limit(2)  # 前日価格
        list_history = [h for h in cur_history]
        return None if not list_history else list_history
