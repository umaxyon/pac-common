from common.util import Util


class TestTest(object):

    def test_get_hash(self):
        actual = Util.get_hash('hoge')
        actual2 = Util.get_hash('hoge')

        assert '-' not in actual
        assert actual == actual2

    def test_is_digit(self):
        assert Util.is_digit('1')
        assert Util.is_digit('-1')
        assert Util.is_digit('1.1')
        assert Util.is_digit('1.')
        assert not Util.is_digit('.1')
        assert not Util.is_digit(' 1')
        assert not Util.is_digit('1 ')
        assert not Util.is_digit('+1')
        assert not Util.is_digit('.')
        assert not Util.is_digit('-')
