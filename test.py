#!/usr/bin/env python
# coding: utf8
import os
from os.path import join
import unittest
import codecs

SRC = "src"


class CheckTemplates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.templates = []

        def ishtml(f):
            return f.endswith(".html")
        for root, _, files in os.walk(SRC):
            cls.templates.extend(filter(ishtml, files))

    def test_templates(self):
        assert len(CheckTemplates.templates) > 40

    def test_all_templates_have_titles_set(self):
        for tfn in CheckTemplates.templates:
            tfnp = join(SRC, tfn)
            t = codecs.open(tfnp, "r", "utf8")
            assert "{% set title=" in t, "No Title for %s" % tfnp


if __name__ == '__main__':
    unittest.main()
