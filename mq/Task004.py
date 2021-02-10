from common.dao import Dao
from common.json import JSON
from common.log import Log
from common.mqpacpac import MqCaller
from common.util import Util
from model.common_model import CommonModel


class Task004(object):
    """
    [task004]ツイート時の株価を取得してreportテーブルに登録する。
    """

    def __init__(self, dao: Dao):
        self.dao = dao
        self.model = CommonModel(dao)

    def run(self, dao: Dao, req):
        Log.info("Task004 invoked.")
        tweet_stocks = req['param']['stocks']
        tweet_id = req['param']['tweet_id']

        for brand in tweet_stocks.values():
            if 'ccode' in brand:
                stock_repos = self.model.find_stock_report_by_ccode(brand['ccode'])
                if stock_repos:
                    result = MqCaller('Task004').call_wait('Task002',
                                                           JSON.dumps([brand['ccode']]), timeout=40)
                    p_dic = JSON.loads(result)
                    if not p_dic or not p_dic['prices']:
                        continue
                    price = p_dic['prices'][brand['ccode']]  # 現在価格
                    history = self.model.find_last_price_history(brand['ccode'])  # 前日と前々日価格
                    if price and history:
                        price = price.replace(',', "")
                        repo_tweets = stock_repos['tweets']
                        for rt in repo_tweets:
                            if rt['id_str'] == tweet_id:
                                Log.debug('price add. price={}, ccode={}, tweet={}',
                                          price, stock_repos['ccode'], tweet_id)
                                if Util.is_digit(price):
                                    Log.debug("price is digit. price={}, history[0][close]={}".format(
                                        price, history[0]['close']))
                                    rt['price'] = int(price)
                                    rt['last_price'] = history[0]['close']
                                    rt['last_price_date'] = history[0]['date']
                                else:
                                    Log.debug("price is not digit. price={}".format(price))
                                    rt['price'] = history[0]['close']
                                    rt['last_price'] = history[1]['close']
                                    rt['last_price_date'] = history[1]['date']

                    self.dao.table('stock_report_pre').update_one(
                        {'ccode': brand['ccode'], 'name': brand['name']},
                        {"$set": stock_repos}, upsert=True)

        Log.info("Task004 end.")


if __name__ == '__main__':
    from common.dao import DB
    from common.mecab_parser import MeCabParser
    from mq.Task001 import Task001

    mecab_parser = MeCabParser()
    dao = Dao(DB())
    task001 = Task001(dao)
    last_data = dao.table('tweet').find({}).sort([
        ('created_at', -1)
    ]).limit(5)
    last_data = [r['id_str'] for r in last_data]

    for id_str in last_data:
        t = task001.find_tweet_by_id(id_str)
        # つぶやきをクリーニング
        task001.tweet_text_cleaning(t)

        # つぶやきを単語分割
        mecab_dic = mecab_parser.parse(t.text)
        # つぶやき内から銘柄取得
        stocks_in_tweet = task001.find_stock_code_in(mecab_dic)
        if stocks_in_tweet:
            Task004(dao).run(dao, {
                "caller": 'test',
                "param": {'stocks': stocks_in_tweet, 'tweet_id': t['id_str']}
            })
