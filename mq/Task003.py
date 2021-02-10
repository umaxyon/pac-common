from datetime import timedelta

from common.dao import Dao
from common.datetime_util import DateTimeUtil
from common.log import Log


class Task003(object):
    """
    [task003]インフルエンサーツイートを集計してtwitter_friendsを更新する。
    """

    def __init__(self, dao: Dao):
        self.dao = dao

    def run(self, dao, req):

        Log.info('twitter_friendsを全件取得。')
        friends = self.dao.table('twitter_friends').find({})

        Log.info('インフルエンサー毎に過去15日のツイートを集計する。')
        for friend in friends:
            cur_repo = self.dao.table('stock_report_pre').find({'tweets.user_id': friend['id_str']})
            month_ago = DateTimeUtil.now() - timedelta(days=15)
            user_tweets = []
            for r in cur_repo:
                u_tws = [t for t in r['tweets'] if t['user_id'] == friend['id_str'] and t['created_at'] >= month_ago]
                if u_tws:
                    ccode_group_list = [t for t in user_tweets if t['ccode'] == r['ccode']]
                    ccode_group = {'name': '', 'last_update_date': month_ago, 'tweet': []}
                    if ccode_group_list:
                        ccode_group = ccode_group_list[0]
                    else:
                        ccode_group['ccode'] = r['ccode']
                        brand = self.dao.table('stock_brands').find_one({'ccode': r['ccode']})
                        if brand:
                            ccode_group['name'] = brand['name']
                        user_tweets.append(ccode_group)

                    ccode_group['last_update_date'] = max(
                        ccode_group['last_update_date'], max([t['created_at'] for t in u_tws]))
                    ccode_group['tweet'].extend(u_tws)

            user_tweets = sorted(user_tweets, key=lambda x: x['last_update_date'], reverse=True)

            ret = []
            for r in user_tweets:
                r['is_market_time'] = DateTimeUtil.is_market_time(r['last_update_date'])
                str_day = r['last_update_date'].strftime('%Y/%m/%d')
                dat = [d for d in ret if d['str_day'] == str_day]
                if dat:
                    dat[0]['tweet'].append(r)
                else:
                    buf = {'str_day': str_day, 'day': r['last_update_date'], 'tweet': [r]}
                    ret.append(buf)

            friend['tweet_summary'] = ret
            dao.table('twitter_friends').update_one({'id_str': friend['id_str']}, {'$set': friend})
            Log.debug('登録: {}', friend['screen_name'])

        Log.info('終了')


if __name__ == '__main__':
    from common.mqpacpac import MqPacPac
    MqPacPac().start({
            'caller': 'JobExp',
            'task': 'Task003',
            'param': None
    })
