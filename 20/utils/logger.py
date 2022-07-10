# -*- coding: utf-8 -*-
from datetime import datetime


class Colors:
    DEFAULT = ''
    WARNING = '\u001b[33;1m'
    OK = '\u001b[32;1m'
    FAIL = '\u001b[31;1m'
    END = '\u001b[0m'


class Logger:
    def __init__(self, prefix=None):
        self.prefix = prefix

    def print(self, text, prefix=None, color=Colors.DEFAULT, log=True, lvl='OK'):
        prefix = prefix if prefix else self.prefix
        date = datetime.now().strftime('[%H:%M:%S]')
        prefix = f'[{prefix}]' if prefix else ''
        print(color + f'{date}{prefix}: {text}' + Colors.END)
        if log:
            self._log(f'{date}{prefix}[{lvl}]: {text}\n')

    def ok(self, text, prefix=None, log=True):
        self.print(text, prefix, Colors.OK, log, 'OK')

    def warn(self, text, prefix=None, log=True):
        self.print(text, prefix, Colors.WARNING, log, 'WARNING')

    def critical(self, text, prefix=None, log=True):
        self.print(text, prefix, Colors.FAIL, log, 'CRITICAL')

    def info(self, text, prefix=None, log=True):
        self.print(text, prefix, Colors.DEFAULT, log, 'INFO')

    def _log(self, text):
        with open('skill.log', 'a', encoding='utf-8') as f:
            f.write(text)
