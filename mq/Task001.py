from attrdict import AttrDict

from common.dao import Dao
from common.log import Log
from common.mecab_parser import MeCabParser
from common.util import Util
from common.mqpacpac import MqCaller
from model.common_model import CommonModel


class Task001(object):
    """
    [task001]ツイート本文を解析してstock_reportにレコードを作る
    """

    def __init__(self, dao: Dao):
        self.dao = dao
        self.model = CommonModel(dao)

    def run(self, dao: Dao, req):
        Log.info("Task001 invoked.")
        mecab_parser = MeCabParser()
        tweet_ids = req['param']
        for id_str in tweet_ids:
            Log.debug('caller={}, reqeust tweet_id={}', req['caller'], id_str)
            t = self.find_tweet_by_id(id_str)

            # つぶやきをクリーニング
            self.tweet_text_cleaning(t)

            # つぶやきを単語分割
            mecab_dic = mecab_parser.parse(t.text)
            # つぶやき内から銘柄取得
            stocks_in_tweet = self.find_stock_code_in(mecab_dic)
            for b in stocks_in_tweet.values():
                Log.info('株 みっけ!! : {} {} user={}', b.ccode, b.name, t.user_name)
                Log.info('tweet={}', t.text)

                stock_repos = self.model.find_stock_report_by_ccode(b.ccode)
                if stock_repos:
                    tweets = list(stock_repos.tweets)
                    if len([tw for tw in tweets if tw['id_str'] == t['id_str']]) == 0:
                        Log.debug('カウントアップ!! : {} {}, user={}', b.ccode, b.name, t.user_name)
                        tweets.append(t)
                        stock_repos.tweets = tweets
                        stock_repos.last_updated_at = t.created_at
                        stock_repos.last_update_user = t.user_id
                        self.upsert_stock_report(b, stock_repos)
                else:
                    Log.debug('初登場!! : {} {}, user={}', b.ccode, b.name, t.user_name)
                    data = {
                        'ccode': b.ccode, 'name': b.name, 'create_user': t.user_id,
                        'created_at': t.created_at, 'last_updated_at': t.created_at,
                        'last_update_user': t.user_id,
                        'tweets': [t]
                    }

                    self.upsert_stock_report(b, data)

                Log.info('Task004に通知')
                MqCaller('Task001').call('Task004', {'stocks': stocks_in_tweet, 'tweet_id': t['id_str']})

        Log.info('Task003に通知')
        MqCaller('Task001').call('Task003', None)

    def find_stock_code_in(self, mecab_dic):
        stocks_in_tweet = {}
        for word, meta in mecab_dic.items():
            Log.debug('「{}」 : {}', word, meta)
            if not meta.get('add1') == '株':
                continue

            b = self.find_brand_by_identify(word)
            if not b:
                continue
            # コードをキーにして、１ツイート内の同一ヒット単語をdistinct
            stocks_in_tweet[b.ccode] = b
        return stocks_in_tweet

    def upsert_stock_report(self, brand, data):
        self.dao.table('stock_report_pre').update_one(
            {'ccode': brand.ccode, 'name': brand.name},
            {"$set": data}, upsert=True)

    def find_brand_by_identify(self, word):
        """stock_brandsのidentifyにつぶやきwordを当てて検索"""
        brands = list(self.dao.table('stock_brands').find({"identify": {"$in": [word]}}, {'_id': 0}))

        if not brands:
            Log.error('wordがstock_brandsに無い。mecab辞書とidentifyが不一致')
            return False
        if len(brands) > 1:
            Log.warn(
                "confrict word!! stock_brandsのidentifyフィールドに同じwordをもつ銘柄がある。 word={}", word)
            return False
        return AttrDict(brands[0])

    def find_tweet_by_id(self, id_str):
        """tweetをidで検索する"""
        cur = self.dao.table('tweet').find({'id_str': id_str})
        tweet = [r for r in cur]
        return {} if not tweet else AttrDict(tweet[0])

    def tweet_text_cleaning(self, t):
        t.text = Util.mask_twitter_name(Util.all_normalize(t.text))


if __name__ == '__main__':
    from common.dao import DB
    from datetime import datetime

    # dao = Dao(DB(path='mongodb://%s:%s@127.0.0.1:29321/dbpacpac' % ('pacPac', 'Npa98ksA')))
    dao = Dao(DB())

    dt = datetime(2018, 3, 9, 9, 34, 22)
    last_data = dao.table('tweet').find({'created_at': {'$gt': dt}}).sort([
        ('created_at', 1)
    ])
    # last_data = list(last_data)
    last_data = [r['id_str'] for r in last_data]

    Task001(dao).run(dao, {
        "caller": 'test',
        "param": last_data
    })
