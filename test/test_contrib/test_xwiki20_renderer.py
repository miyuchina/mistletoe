from test.base_test import BaseRendererTest
from mistletoe.span_token import tokenize_inner
from mistletoe.contrib.xwiki20_renderer import XWiki20Renderer
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
        output = self.renderer.render(token)
        expected = outputTemplate.format(input)
        self.assertEqual(output, expected)

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
        output = self.renderer.render(token)
        expected = '[[image:foo.jpg]]'
        self.assertEqual(output, expected)

    def test_render_link(self):
        url = 'http://{0}.{1}.{2}'.format(self.genRandomString(5), self.genRandomString(5), self.genRandomString(3))
        body = self.genRandomString(80, True)
        token = next(iter(tokenize_inner('[{body}]({url})'.format(url=url, body=body))))
        output = self.renderer.render(token)
        expected = '[[{body}>>{url}]]'.format(url=url, body=body)
        self.assertEqual(output, expected)

    def test_render_auto_link(self):
        url = 'http://{0}.{1}.{2}'.format(self.genRandomString(5), self.genRandomString(5), self.genRandomString(3))
        token = next(iter(tokenize_inner('<{url}>'.format(url=url))))
        output = self.renderer.render(token)
        expected = '[[{url}]]'.format(url=url)
        self.assertEqual(output, expected)

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
