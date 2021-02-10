import freezegun

from common.datetime_util import DailyTrigger
from common.datetime_util import DayOfWeek


class TestDailyTrigger(object):

    def test_daily_trigger_1(self):
        # 0時1分のトリガーを作成
        trigger = DailyTrigger.of(0, 1)

        with freezegun.freeze_time('2018-01-01 00:01:00') as freeze_datetime:
            # 現在は0時1分(トリガー時刻と同時刻）
            assert trigger.is_performed() == True  # 初回のみTrue
            assert trigger.is_performed() == False  # 2度目以降はFalse
            assert trigger.is_performed() == False

        with freezegun.freeze_time('2018-01-02 00:00:00') as freeze_datetime:
            # 23時間59分進める(日付変わる)
            assert trigger.is_performed() == False

        with freezegun.freeze_time('2018-01-02 00:01:00') as freeze_datetime:
            # さらに1分進める(24時間経過)
            assert trigger.is_performed() == True  # 初回のみTrue
            assert trigger.is_performed() == False  # 2度目以降はFalse
            assert trigger.is_performed() == False

    def test_daily_trigger_2(self):
        # 火、金のみ18時30分のトリガーを作成
        trigger = DailyTrigger.of(18, 30, DayOfWeek.Tuesday, DayOfWeek.Friday)

        with freezegun.freeze_time('2018-02-05 00:18:29') as freeze_datetime:
            # 現在は5日(月)の18時29分
            assert trigger.is_performed() == False

        with freezegun.freeze_time('2018-02-05 18:30:00') as freeze_datetime:
            # トリガー時刻(18時30分)だが月曜なのでFalse
            assert trigger.is_performed() == False

        with freezegun.freeze_time('2018-02-06 18:29:00') as freeze_datetime:
            # 現在は6日(火)の18時29分
            assert trigger.is_performed() == False

        with freezegun.freeze_time('2018-02-06 18:30:00') as freeze_datetime:
            # 現在は6日(火)のトリガー時刻(18時30分)
            assert trigger.is_performed() == True  # 初回のみ True
            # assert trigger.is_performed() == False

        with freezegun.freeze_time('2018-02-09 18:30:00') as freeze_datetime:
            # 現在は9日(金)のトリガー時刻(18時30分)
            assert trigger.is_performed() == True  # 初回のみ True(前回Trueから一度もFalseに振れてなくてもOK)
            assert trigger.is_performed() == False

        with freezegun.freeze_time('2018-02-11 18:30:00') as freeze_datetime:
            # トリガー時刻(18時30分)だが日曜なのでFalse
            assert trigger.is_performed() == False
