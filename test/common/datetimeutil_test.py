from datetime import datetime
from common.datetime_util import DateTimeUtil


class TestDateTimeUtil(object):

    def test_date_from_japanese_era1(self):
        assert DateTimeUtil.date_from_japanese_era('平成30年2月22日') == datetime(2018, 2, 22)
        assert DateTimeUtil.date_from_japanese_era('平成11年12月31日') == datetime(1999, 12, 31)
        assert DateTimeUtil.date_from_japanese_era('平成12年1月1日') == datetime(2000, 1, 1)
        assert DateTimeUtil.date_from_japanese_era('昭和1年5月6日') == datetime(1926, 5, 6)
        assert DateTimeUtil.date_from_japanese_era('昭和64年1月1日') == datetime(1989, 1, 1)
        assert DateTimeUtil.date_from_japanese_era('平成1年1月1日') == datetime(1989, 1, 1)
        assert DateTimeUtil.date_from_japanese_era('平成1年1月日') is None
        assert DateTimeUtil.date_from_japanese_era('平成1年月2日') is None
        assert DateTimeUtil.date_from_japanese_era('2011年1月2日') is None

    def test_strf_mda_hm(self):
        assert DateTimeUtil.strf_mda_hm(datetime(2018, 12, 12, 15, 14, 20)) == '12/12(水) 15:14'
        assert DateTimeUtil.strf_mda_hm(datetime(2018, 2, 1, 5, 4, 20)) == '2/1(木) 5:04'

    def test_is_market_time(self):
        # 3/3(土)
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 3, 8, 59, 59))
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 3, 9, 00, 00))
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 3, 14, 59, 59))
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 3, 15, 00, 00))
        # 3/4(日)
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 4, 8, 59, 59))
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 4, 9, 00, 00))
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 4, 14, 59, 59))
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 4, 15, 00, 00))
        # 3/5(月)
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 5, 8, 59, 59))
        assert DateTimeUtil.is_market_time(datetime(2018, 3, 5, 9, 00, 00))
        assert DateTimeUtil.is_market_time(datetime(2018, 3, 5, 14, 59, 59))
        assert not DateTimeUtil.is_market_time(datetime(2018, 3, 5, 15, 00, 00))
