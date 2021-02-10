# coding:utf-8
import re
import os
import requests
from natto import MeCab

from common.const import TEST_USER_AGENT
from common.const import MECAB_API_URL
from common.const import PTN_URL
from common.const import PTN_FIGURE


class RemoteMecabParser(object):
    def parse(self, text):
        headers = {
            'User-Agent': TEST_USER_AGENT,
            'Accept': 'application/json',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/json; charset=UTF-8'
        }

        r = requests.post(
            MECAB_API_URL,
            # 'http://localhost:8000/mecab/mecab/api/',
            headers=headers,
            data={
                'text': text,
            })
        return r.text


class MeCabParser(object):
    def __init__(self):
        if os.name == 'nt':
            self.engine = RemoteMecabParser()
        else:
            self.engine = MeCab()

    def parse(self, text):
        masked_text, urls = self.url_mask(text)
        masked_text, figures = self.figure_mask(masked_text)
        masked_text, digits = self.digit_mask(masked_text)

        mc_ret = self.engine.parse(masked_text)
        mc_lines = mc_ret.split('\n')
        dic = {}
        for line in mc_lines:
            s = line.split('\t')
            if len(s) >= 2:
                buf = s[1].split(',')
                meta = {'part1': buf[0], 'part2': buf[1], 'part3': buf[2]}
                if len(buf) > 9:
                    meta['add1'] = buf[9]
                key = s[0]
                if key == 'PACMECABURL':
                    key = urls.pop(0)
                if key == 'PACMECABFIGURE':
                    key = figures.pop(0)
                if key == 'PACMECABDIGIT':
                    key = digits.pop(0)
                dic[key] = meta  # 同じwordはキーとしてdistinctされる

        return dic

    def url_mask(self, text):
        match = re.findall(PTN_URL, text)
        for m in match:
            text = text.replace(m, 'PACMECABURL')

        return text, match

    def figure_mask(self, text):
        match_list = []
        for ptn in PTN_FIGURE:
            match = re.findall(ptn, text)
            for m in match:
                text = text.replace(m, 'PACMECABFIGURE')
            match_list += match
        return text, match_list

    def digit_mask(self, text):
        match = re.findall('\d{5,}', text)
        for m in match:
            text = text.replace(m, 'PACMECABDIGIT')
        return text, match
