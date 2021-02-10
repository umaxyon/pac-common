import json
import sys

import requests

from common.const import RedisDB
from common.logic.scraping import Scraping
from common.time_cache import TimeCache


class Task002(object):
    """
    [task002]証券コードリストを受け取り、Yahooファイナンスの現在株価をスクレイピングする。
    """

    def __init__(self, dao):
        self.dao = dao
        self.tc = TimeCache(cleartime=240, db=RedisDB.Now_stock_price.value)

    def run(self, dao, req):
        ccode_list = json.loads(req['param'], encoding='UTF-8')
        ret = dict()
        for ccode in ccode_list:
            price = self.tc.get(ccode)
            if price is None:
                try:
                    url = "https://stocks.finance.yahoo.co.jp/stocks/detail/"
                    html = requests.get(url, {'code': ccode}, timeout=15)
                    price = Scraping.get_now_price_from_yahoo_stock_detail(html.text)
                    self.tc.set(ccode, price)
                except:
                    e = sys.exc_info()
                    print("error!! {}".format(e))
                    price = "--"
            ret[ccode] = price

        return json.dumps({'prices': ret})
