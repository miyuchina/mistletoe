from contrib.limited_html_renderer import LimitedHTMLRenderer
from mistletoe.block_token import Document
import random
import string
from unittest import TestCase

class TestLimitedHTMLRenderer(TestCase):
    def setUp(self):
        self.renderer = LimitedHTMLRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def check_render(self, inputString, expected, errormsg):
        output = self.renderer.render(Document(inputString))
        output = output.strip()
        self.assertEqual(output, expected, errormsg)

    def test_render_inline_div(self):
        input = '<div>hello</div>'
        output = '&lt;div&gt;hello&lt;/div&gt;'
        self.check_render(input, output, 'One line div is not escaped')

    def test_render_inline_span(self):
        input = '<span>hello</span>'
        output = '<p>&lt;span&gt;hello&lt;/span&gt;</p>'
        self.check_render(input, output, 'One line span is not escaped')

    def test_render_embedded_markdown(self):
        input = '<div>\n\n*hello*\n\n</div>'
        output = '&lt;div&gt;\n<p><em>hello</em></p>\n&lt;/div&gt;'
        self.check_render(input, output, 'Markdown inside div is unexpectedly escaped')
