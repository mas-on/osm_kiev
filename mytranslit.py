#!/usr/bin/python
# -*- coding: utf-8 -*-
from transliterate.discover import autodiscover
autodiscover()

from transliterate.base import TranslitLanguagePack, registry
from transliterate import translit

class ImprovedRussianLanguagePack(TranslitLanguagePack):
    language_code = "ru_new"
    language_name = "Improved Russian"
    mapping = (
       u"abvgdeziiklmnoprstuf'yABVGDEZIIKLMNOPRSTUFY", # Source script
       u"абвгдезийклмнопрстуфъыАБВГДЕЗИЙКЛМНОПРСТУФЫ", # Target script
    )
    pre_processor_mapping = {
        u"ya": u"я",
        u"zh": u"ж",
        u"ia": u"я",
        u"yo": u"ё",
        u"kh": u"х",
        u"ts": u"ц",
        u"ch": u"ч",
        u"sh": u"ш",
        u"sch": u"щ",
        u"yu": u"ю",
        u"Ya": u"Я",
        u"Zh": u"Ж",
        u"Yo": u"Ё",
        u"Kh": u"Х",
        u"Ts": u"Ц",
        u"Ch": u"Ч",
        u"Sh": u"Ш",
        u"Sch": u"Щ",
        u"Yu": u"Ю"
    }

def translit2ru(s):
    registry.register(ImprovedRussianLanguagePack)
    return translit(s.replace(u"zhy",u"жи").replace(u"Zhy",u"Жи"), 'ru_new')

def translit2uk(s):
    return translit(s,'uk')