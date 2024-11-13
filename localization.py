import json
import locale
import sys

_LOCALE_DEFAULT = 'en_US'
_LOCALE_PATH = 'locale'


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class L10N:
    def __init__(self):
        code, _ = locale.getdefaultlocale()
        self.messages = self._load_locale(code)
        self.messages_default = self._load_locale(_LOCALE_DEFAULT)

    def _load_locale(self, code):
        try:
            filepath = f'{sys._MEIPASS}/{code}.json' if is_bundled(
            ) else f'{_LOCALE_PATH}/{code}.json'
            with open(filepath, encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return dict()

    def text(self, key):
        return self.messages.get(key, self.messages_default.get(key, key))


def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
