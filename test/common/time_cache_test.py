import time
import freezegun
from common.time_cache import TimeCache
from common.datetime_util import OrdinaryDaysTrigger


class TestTimeCache(object):

    def test_timecache1(self):
        tc = TimeCache(cleartime=2)
        tc.set('test', 'hoge')
        assert tc.get('test') == 'hoge'

    def test_timecache2(self):
        tc = TimeCache(cleartime=2)
        tc.set('test', 'hoge')
        tc.set('test', 'huga')
        assert tc.get('test') == 'huga'

    def test_timecache3(self):
        tc = TimeCache(cleartime=2)
        tc.set('test', 'hoge')
        time.sleep(3)
        assert tc.get('test') is None

    def test_timecache4(self):
        tc1 = TimeCache(cleartime=2)
        tc2 = TimeCache(cleartime=2, db=1)
        tc1.set('test', 'hoge')
        tc2.set('test', 'huga')
        assert tc1.get('test') == 'hoge'
        assert tc2.get('test') == 'huga'

    def test_timecache5(self):
        tc = TimeCache(trigger=OrdinaryDaysTrigger)

        with freezegun.freeze_time('2018-02-05 00:00:00') as freeze_datetime:
            # 現在は2月5日(月)
            tc.set('test', 'hoge')
            assert tc.get('test') == 'hoge'

        with freezegun.freeze_time('2018-02-05 23:59:59') as freeze_datetime:
            # 現在は2月5日(月) 23時59分59秒
            assert tc.get('test') == 'hoge'

        with freezegun.freeze_time('2018-02-06 00:00:00') as freeze_datetime:
            # 現在は2月6日(火)
            assert tc.get('test') is None  # キャッシュ消える
            tc.set('test', 'hoge2')
            assert tc.get('test') == 'hoge2'
            assert tc.get('test') == 'hoge2'

        with freezegun.freeze_time('2018-02-09 00:00:00') as freeze_datetime:
            # 現在は2月9日(金)
            assert tc.get('test') is None  # キャッシュ消える
            tc.set('test', 'hoge3')
            assert tc.get('test') == 'hoge3'

        with freezegun.freeze_time('2018-02-10 00:00:00') as freeze_datetime:
            # 現在は2月10日(土)
            assert tc.get('test') == 'hoge3'  # キャッシュ消えない

        with freezegun.freeze_time('2018-02-11 00:00:00') as freeze_datetime:
            # 現在は2月11日(日)
            assert tc.get('test') == 'hoge3'  # キャッシュ消えない

        with freezegun.freeze_time('2018-02-12 00:00:00') as freeze_datetime:
            # 現在は2月12日(月)
            assert tc.get('test') is None  # キャッシュ消える
