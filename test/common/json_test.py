from common.json import JSON
from datetime import datetime


class TestJson(object):

    def test_json1(self):
        data = {'key1': 'hoge',
                'date': datetime(2018, 1, 1, 10, 12, 5, 0)}
        str_json = JSON.dumps(data)
        # datetimeがJSON化できる
        assert str_json == '{"key1": "hoge", "date": "2018/01/01_10:12:05"}'

        # 指定フィールドの日付文字列をdatetimeに戻してloadできる
        actual = JSON.loads(str_json, ['date'])
        assert actual == data

    def test_json2(self):
        data = {'key1': 'hoge',
                'ob': {
                    'date': datetime(2018, 1, 1, 10, 12, 5, 0)
                },
                'date': datetime(2018, 1, 1, 10, 12, 6, 0)}
        str_json = JSON.dumps(data)
        # 入れ子オブジェクトでもJSON化できる
        assert str_json == '{"key1": "hoge", "ob": {"date": "2018/01/01_10:12:05"}, "date": "2018/01/01_10:12:06"}'

        # 入れ子でも戻せる
        actual = JSON.loads(str_json, ['date', 'ob.date'])
        assert actual == data

    def test_json3(self):
        data = {'key1': 'hoge',
                'ob': [
                    {'date': datetime(2018, 1, 1, 10, 12, 5, 0)},
                    {'date': datetime(2018, 1, 1, 10, 12, 6, 0)}
                ],
                'date': datetime(2018, 1, 1, 10, 12, 7, 0)}
        str_json = JSON.dumps(data)
        # list in dictでもJSON化できる
        assert str_json == ('{"key1": "hoge", "ob": ['
                            '{"date": "2018/01/01_10:12:05"},'
                            ' {"date": "2018/01/01_10:12:06"}],'
                            ' "date": "2018/01/01_10:12:07"}')

        # list in dictでも戻せる
        actual = JSON.loads(str_json, ['date', 'ob.date'])
        assert actual == data
