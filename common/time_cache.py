# coding:utf-8
import redis
from datetime import datetime
from common.datetime_util import DailyTrigger
from common.datetime_util import DateTimeUtil


class TimeCache(object):

    def __init__(self, cleartime=0, trigger=None, db=0):
        self.db = redis.Redis(host='localhost', port=6379, db=db)
        self.cleartime = cleartime
        self.trigger: DailyTrigger = trigger

    @classmethod
    def create_daily_cache(cls, trigger: DailyTrigger, db=0):
        return TimeCache(trigger=trigger, db=db)

    @classmethod
    def create_second_cache(cls, cleartime, db=0):
        return TimeCache(cleartime=cleartime, db=db)

    def clear(self):
        self.db.flushall()

    def set(self, key, val):
        self.db.hset(key, 'val', val)
        self.db.hset(key, 'ct', datetime.now().strftime('%Y/%m/%d'))

        if self.cleartime > 0:
            self.db.expire(key, self.cleartime)

    def get(self, key):
        if self.trigger is not None:
            return self._daily_get(key)
        else:
            return self._get_val(key)

    def _get_val(self, key):
        try:
            data = self.db.hget(key, 'val')
            return None if data is None else data.decode()
        except:
            return None

    def _daily_get(self, key):
        if self.trigger.is_weekday():
            tm = self.db.hget(key, 'ct')
            if tm is not None:
                save_day = datetime.strptime(tm.decode(), '%Y/%m/%d').date()
                if save_day < DateTimeUtil.today().date():
                    self.db.delete(key)
                    return None
        return self._get_val(key)
