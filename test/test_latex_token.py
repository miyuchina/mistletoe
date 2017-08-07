import unittest
import test.helpers as helpers
import mistletoe.span_token as span_token
import mistletoe.latex_token as latex_token
from mistletoe.latex_renderer import LaTeXRenderer

class TestLaTeXToken(unittest.TestCase):
    def test_span(self):
        with LaTeXRenderer():
            t = span_token.Strong('$ 1 + 2 = 3 $')
            c = span_token.Math('$ 1 + 2 = 3 $')
            helpers.check_equal(self, list(t.children)[0], c)
