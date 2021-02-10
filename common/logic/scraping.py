import re

from common.util import Util


class Scraping(object):

    @staticmethod
    def get_now_price_from_yahoo_stock_detail(html):
        """Yahooファイナンスの銘柄ページのHTMLから現在株価を取得する"""
        m = re.search('<td class="stoksPrice">(.+)</td>', html)
        if m:
            price = m.group(1).replace(',', '')
            price = re.sub('\.\d*$', '', price)
            if Util.is_digit(price):
                return price
        return ""
