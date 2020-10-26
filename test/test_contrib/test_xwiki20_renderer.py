# Copyright 2018 Tile, Inc.  All Rights Reserved.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from unittest import TestCase, mock
from test.base_test import BaseRendererTest
from mistletoe.block_token import Document
from mistletoe.span_token import tokenize_inner
from mistletoe import Document
from contrib.xwiki20_renderer import XWiki20Renderer
import random
import string

filesBasedTest = BaseRendererTest.filesBasedTest

class TestXWiki20Renderer(BaseRendererTest):

    def setUp(self):
        super().setUp()
        self.renderer = XWiki20Renderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)
        self.sampleOutputExtension = 'xwiki20'

    def genRandomString(self, n, hasWhitespace=False):
        source = string.ascii_letters + string.digits
        if hasWhitespace:
            source = source + ' \t'
        
        result = ''.join(random.SystemRandom().choice(source) for _ in range(n))
        return result

    def textFormatTest(self, inputTemplate, outputTemplate):
        input = self.genRandomString(80, False)
        token = next(iter(tokenize_inner(inputTemplate.format(input))))
        expected = outputTemplate.format(input)
        actual = self.renderer.render(token)
        self.assertEqual(expected, actual)

    def test_escaping(self):
        self.textFormatTest('**code: `a = 1;// comment`, plain text URL: http://example.com**',
                '**code: {{{{code}}}}a = 1;// comment{{{{/code}}}}, plain text URL: http:~//example.com**')

    def test_render_strong(self):
        self.textFormatTest('**a{}**', '**a{}**')

    def test_render_emphasis(self):
        self.textFormatTest('*a{}*', '//a{}//')
        
    def test_render_inline_code(self):
        self.textFormatTest('`a{}b`', '{{{{code}}}}a{}b{{{{/code}}}}')

    def test_render_strikethrough(self):
        self.textFormatTest('~~{}~~', '--{}--')

    def test_render_image(self):
        token = next(iter(tokenize_inner('![image](foo.jpg)')))
        expected = '[[image:foo.jpg]]'
        actual = self.renderer.render(token)
        self.assertEqual(expected, actual)
    
    def test_render_link(self):
        url = 'http://{0}.{1}.{2}'.format(self.genRandomString(5), self.genRandomString(5), self.genRandomString(3))
        body = self.genRandomString(80, True)
        token = next(iter(tokenize_inner('[{body}]({url})'.format(url=url, body=body))))
        expected = '[[{body}>>{url}]]'.format(url=url, body=body)
        actual = self.renderer.render(token)
        self.assertEqual(expected, actual)
    
    def test_render_auto_link(self):
        url = 'http://{0}.{1}.{2}'.format(self.genRandomString(5), self.genRandomString(5), self.genRandomString(3))
        token = next(iter(tokenize_inner('<{url}>'.format(url=url))))
        expected = '[[{url}]]'.format(url=url)
        actual = self.renderer.render(token)
        self.assertEqual(expected, actual)

    def test_render_html_span(self):
        markdown = 'text styles: <i>italic</i>, <b>bold</b>'
        # See fixme at the `render_html_span` method...
        # expected = 'text styles: {{html wiki="true"}}<i>italic</i>{{/html}}, {{html wiki="true"}}<b>bold</b>{{/html}}\n\n'
        expected = 'text styles: <i>italic</i>, <b>bold</b>\n\n'
        self.markdownResultTest(markdown, expected)
    
    def test_render_html_block(self):
        markdown = 'paragraph\n\n<pre>some <i>cool</i> code</pre>'
        expected = 'paragraph\n\n{{html wiki="true"}}\n<pre>some <i>cool</i> code</pre>\n{{/html}}\n\n'
        self.markdownResultTest(markdown, expected)
    
    def test_render_xwiki_macros_simple(self):
        markdown = """\
{{warning}}
Use this feature with *caution*. See {{Wikipedia article="SomeArticle"/}}. {{test}}Another inline macro{{/test}}.
{{/warning}}
"""
        # Note: There is a trailing ' ' at the end of the second line. It will be a bit complicated to get rid of it.
        expected = """\
{{warning}}
Use this feature with //caution//. See {{Wikipedia article="SomeArticle"/}}. {{test}}Another inline macro{{/test}}. \n\
{{/warning}}

"""
        self.markdownResultTest(markdown, expected)
    
    def test_render_xwiki_macros_in_list(self):
        markdown = """\
* list item

  {{warning}}
  Use this feature with *caution*. See {{Wikipedia article="SomeArticle"/}}. {{test}}Another inline macro{{/test}}.
  {{/warning}}
"""
        # Note: There is a trailing ' ' at the end of the second line. It will be a bit complicated to get rid of it.
        expected = """\
* list item(((
{{warning}}
Use this feature with //caution//. See {{Wikipedia article="SomeArticle"/}}. {{test}}Another inline macro{{/test}}. \n\
{{/warning}}
)))

"""
        self.markdownResultTest(markdown, expected)
    
    @filesBasedTest
    def test_render__basic_blocks(self):
        pass

    @filesBasedTest
    def test_render__lists(self):
        pass

    @filesBasedTest
    def test_render__quotes(self):
        pass
