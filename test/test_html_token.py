import unittest
import test.helpers as helpers
import mistletoe.span_token as span_token
import mistletoe.block_token as block_token
import mistletoe.html_token

class TestHTMLTokenizer(unittest.TestCase):
    def test_span(self):
        raw = 'some <span>more</span> text'
        t = span_token.Strong(raw)
        c0 = span_token.RawText('some ')
        c1 = span_token.HTMLSpan('<span>more</span>')
        c2 = span_token.RawText(' text')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)

    def test_block(self):
        lines = ['# heading 1\n',
                 '\n',
                 '<p> a paragraph\n',
                 'within an html block\n',
                 '</p>\n']
        t = block_token.Document(lines)
        c0 = block_token.Heading(lines[:1])
        c1 = block_token.HTMLBlock(lines[2:])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)

    def test_span_attrs(self):
        raw = 'some <span class="foo">more</span> text'
        t = span_token.Strong(raw)
        c0 = span_token.RawText('some ')
        c1 = span_token.HTMLSpan('<span class="foo">more</span>')
        c2 = span_token.RawText(' text')
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
        helpers.check_equal(self, l[2], c2)

    def test_block_attrs(self):
        lines = ['# heading 1\n',
                 '\n',
                 '<p class="bar"> a paragraph\n',
                 'within an html block\n',
                 '</p>\n']
        t = block_token.Document(lines)
        c0 = block_token.Heading(lines[:1])
        c1 = block_token.HTMLBlock(lines[2:])
        l = list(t.children)
        helpers.check_equal(self, l[0], c0)
        helpers.check_equal(self, l[1], c1)
