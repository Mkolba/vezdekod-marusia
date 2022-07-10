# -*- coding: utf-8 -*-
from datetime import datetime
from random import choice
import json
import re


tts_nums = {
    '1': 'одну',
    '2': 'две',
    '3': 'три',
    '4': 'четыре',
    '5': 'пять',
    '6': 'шесть',
    '7': 'семь',
    '8': 'восемь',
    '9': 'девять',
    '10': 'десять',
    '11': 'одинадцать',
    '12': 'двенадцать',
    '13': 'тринадцать',
    '14': 'четырнадцать',
    '15': 'пятнадцать',
}


stop_words = ['стоп', 'выход', 'закончить', 'выйти']


class BetterDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    @staticmethod
    def loads(obj):
        return json.loads(obj, object_pairs_hook=lambda x: BetterDict(x))


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.timestamp()
    raise TypeError("Type %s not serializable" % type(obj))


def prepare_text(string):
    return string.replace("^", "")


def prepare_tts(string):
    numbers = set(re.findall('(?:^|\s)(\d+)(?:$|\s)', string))
    for number in numbers:
        if number in tts_nums:
            string = string.replace(number, tts_nums[number])
    return string.replace('"', "").replace("«", "").replace("»", "")


def incline_score(num):
    text_forms = ['очко', 'очков', 'очков']
    n = abs(num) % 100
    n1 = n % 10
    if 10 < n < 20:
        return text_forms[2]
    if 1 < n1 < 5:
        return text_forms[1]
    if n1 == 1:
        return text_forms[0]
    return text_forms[2]


def is_stop_word(word):
    for i in stop_words:
        if i in word:
            return True
