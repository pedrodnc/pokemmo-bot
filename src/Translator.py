import json


class Translator:
    def __init__(self, lang) -> None:
        self.lang = lang

    def t(self, pattern):
        keys = pattern.split('.')
        current_dict = self.lang
        for key in keys:
            current_dict = current_dict[key]
        return current_dict
