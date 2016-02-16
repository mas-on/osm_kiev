#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase
from mytranslit import translit2ru, translit2uk

class TestMyTranslit(TestCase):
    def test_translit2ru(self):
        self.assertEqual(translit2ru(u'zhylianskaya'), u'жилянская')
        self.assertEqual(translit2ru(u'Zhylianskaya'), u'Жилянская')
        self.assertEqual(translit2ru(u'gertsena'), u'герцена')


    def test_translit2uk(self):
        self.assertEqual(translit2uk(u'Gogolevska'), u'Ґоґолевска')
