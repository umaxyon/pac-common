# coding:utf-8
import re
from datetime import datetime
from datetime import time
from datetime import timedelta
from tzlocal import get_localzone
from enum import Enum


class DateTimeUtil(object):

    @staticmethod
    def today():
        return datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def now():
        return datetime.now(get_localzone())

    @staticmethod
    def yesterday():
        return DateTimeUtil.prevday(1)

    @staticmethod
    def nextday(cnt):
        return DateTimeUtil.now() + timedelta(days=cnt)

    @staticmethod
    def prevday(cnt):
        return DateTimeUtil.now() - timedelta(days=cnt)

    @staticmethod
    def tommorow():
        return DateTimeUtil.nextday(1)

    @staticmethod
    def one_hour_ago():
        return DateTimeUtil.now() - timedelta(hours=1)

    @staticmethod
    def one_hour_later():
        return DateTimeUtil.now() + timedelta(hours=1)

    @staticmethod
    def minute_ago(cnt):
        return DateTimeUtil.now() - timedelta(minutes=cnt)

    @staticmethod
    def minute_later(cnt):
        return DateTimeUtil.now() + timedelta(minutes=cnt)

    @staticmethod
    def one_month():
        return timedelta(days=30)

    @staticmethod
    def strf_ymd(dt: datetime):
        return dt.strftime('%Y/%m/%d')

    @staticmethod
    def strf_mda_hm(dt: datetime):
        """月日時にゼロ埋め無しのフォーマット"""
        f = dt.strftime('{}/{}({}) {}:%M')
        w = DayOfWeek.from_date(dt).to_japanese()
        return f.format(dt.month, dt.day, w, dt.hour)

    @staticmethod
    def is_market_time(dt: datetime):
        """月～金の9:00～15:00はTrue"""
        if DayOfWeek.from_date(dt) not in DayOfWeek.weekday():
            return False
        t = dt.strftime('%H:%M:%S')
        return '09:00:00' <= t < '15:00:00'

    @staticmethod
    def date_from_japanese_era(japanese_str):
        m = re.search('(\D\D)(\d+)年(\d+)月(\d+)日', japanese_str)
        if not m:
            return None
        era, year, month, date = m.group(1), m.group(2), m.group(3), m.group(4)
        if era == '平成':
            buf = int(year) + 88
            if buf >= 100:
                year = int('20' + str(buf)[-2:])
            else:
                year = int('19' + str(buf))
        elif era == '昭和':
            year = 1900 + int(year) + 25

        return datetime(year, int(month), int(date))


class DayOfWeek(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

    def iso_value(self):
        return self.value + 1

    def to_japanese(self):
        return '月火水木金土日'[self.value]

    @property
    def shortname(self):
        return self.name[:3]

    @classmethod
    def from_date(cls, d: datetime):
        return cls(d.weekday())

    @classmethod
    def all(cls):
        return (cls.Monday,
                cls.Tuesday,
                cls.Wednesday,
                cls.Thursday,
                cls.Friday,
                cls.Saturday,
                cls.Sunday,)

    @classmethod
    def weekday(cls):
        return (cls.Monday,
                cls.Tuesday,
                cls.Wednesday,
                cls.Thursday,
                cls.Friday,)

    @classmethod
    def holiday(cls):
        return (cls.Saturday,
                cls.Sunday,)


class DailyTrigger(object):
    _trigger = False
    _last_exec_date = None
    _time = None

    def __init__(self, t: time, weekday):
        self._time = t
        self._weekdays = weekday if weekday else DayOfWeek.all()

    @staticmethod
    def of(hour=0, minute=0, *weekday):
        t = time(hour, minute, 0)
        return DailyTrigger(t, *weekday)

    def is_performed(self):
        """（指定曜日内の）１日の中で、指定時刻を過ぎた１回目の呼び出しのみTrueを返す。"""
        now = datetime.now()
        if not self.is_weekday(now):
            return False

        if self._trigger:
            if self._last_exec_date.day < now.day:
                self._trigger = False

        if not self._trigger:
            if now.time() >= self._time:
                self._trigger = True
                self._last_exec_date = DateTimeUtil.today()
                return True
        return False

    def is_weekday(self, target_day: datetime = None):
        """ 指定日が指定曜日の場合にTrueを返す。"""
        dt = target_day if target_day is not None else DateTimeUtil.today()
        return DayOfWeek(dt.weekday()) in self._weekdays


# 平日判定用トリガー
OrdinaryDaysTrigger = DailyTrigger.of(0, 0, DayOfWeek.weekday())
