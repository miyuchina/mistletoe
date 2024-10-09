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

from test.base_test import BaseRendererTest
from mistletoe.span_token import tokenize_inner
from mistletoe.contrib.jira_renderer import JiraRenderer
import random
import string

filesBasedTest = BaseRendererTest.filesBasedTest


class TestJiraRenderer(BaseRendererTest):

    def setUp(self):
        super().setUp()
        self.renderer = JiraRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)
        self.sampleOutputExtension = 'jira'

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

    def test_escape_simple(self):
        self.textFormatTest('---fancy text---', '\\-\\-\\-fancy text\\-\\-\\-')

    def test_escape_single_chars(self):
        self.textFormatTest('**fancy \\*@\\* text**', '*fancy \\*@\\* text*')

    def test_escape_none_when_whitespaces(self):
        self.textFormatTest('obj = {{ a: (b * c) + d }}', 'obj = {{ a: (b * c) + d }}')

    def test_escape_in_inline_code(self):
        # Note: Jira puts inline code into "{{...}}" as seen in this test.
        self.textFormatTest('**code: `a = b + c;// [1]`**',
                '*code: {{{{a = b + c;// \\[1\\]}}}}*')

    def test_escape_link(self):
        # Note: There seems to be no way of how to escape plain text URL in Jira.
        self.textFormatTest('http://www.example.com', 'http://www.example.com')

    def test_render_strong(self):
        self.textFormatTest('**a{}**', '*a{}*')

    def test_render_emphasis(self):
        self.textFormatTest('*a{}*', '_a{}_')

    def test_render_inline_code(self):
        self.textFormatTest('`a{}b`', '{{{{a{}b}}}}')

    def test_render_strikethrough(self):
        self.textFormatTest('~~{}~~', '-{}-')

    def test_render_image(self):
        token = next(iter(tokenize_inner('![image](foo.jpg)')))
        output = self.renderer.render(token)
        expected = '!foo.jpg!'
        self.assertEqual(output, expected)

    def test_render_footnote_image(self):
        # token = next(tokenize_inner('![image]\n\n[image]: foo.jpg'))
        # output = self.renderer.render(token)
        # expected = '!foo.jpg!'
        # self.assertEqual(output, expected)
        pass

    def test_render_link(self):
        url = 'http://{0}.{1}.{2}'.format(self.genRandomString(5), self.genRandomString(5), self.genRandomString(3))
        body = self.genRandomString(80, True)
        token = next(iter(tokenize_inner('[{body}]({url})'.format(url=url, body=body))))
        output = self.renderer.render(token)
        expected = '[{body}|{url}]'.format(url=url, body=body)
        self.assertEqual(output, expected)

    def test_render_link_with_title(self):
        url = 'http://{0}.{1}.{2}'.format(self.genRandomString(5), self.genRandomString(5), self.genRandomString(3))
        body = self.genRandomString(80, True)
        title = self.genRandomString(20, True)
        token = next(iter(tokenize_inner('[{body}]({url} "{title}")'.format(url=url, body=body, title=title))))
        output = self.renderer.render(token)
        expected = '[{body}|{url}|{title}]'.format(url=url, body=body, title=title)
        self.assertEqual(output, expected)

    def test_render_footnote_link(self):
        pass

    def test_render_auto_link(self):
        url = 'http://{0}.{1}.{2}'.format(self.genRandomString(5), self.genRandomString(5), self.genRandomString(3))
        token = next(iter(tokenize_inner('<{url}>'.format(url=url))))
        output = self.renderer.render(token)
        expected = '[{url}]'.format(url=url)
        self.assertEqual(output, expected)

    def test_render_escape_sequence(self):
        pass

    def test_render_html_span(self):
        pass

    def test_render_heading(self):
        pass

    def test_render_quote(self):
        pass

    def test_render_paragraph(self):
        pass

    def test_render_block_code(self):
        markdown = """\
```java
public static void main(String[] args) {
    // a = 1 * 2;
}
```
"""
        expected = """\
{code:java}
public static void main(String[] args) {
    // a = 1 * 2;
}
{code}

"""
        self.markdownResultTest(markdown, expected)

    def test_render_list(self):
        pass

    def test_render_list_item(self):
        pass

    def test_render_inner(self):
        pass

    def test_render_table(self):
        pass

    def test_render_table_row(self):
        pass

    def test_render_table_cell(self):
        pass

    def test_render_thematic_break(self):
        pass

    def test_render_html_block(self):
        pass

    def test_render_document(self):
        pass

    def test_table_header(self):
        markdown = """\
| header row   |
|--------------|
| first cell   |
"""
        expected = """\
||header row||
|first cell|

"""
        self.markdownResultTest(markdown, expected)

    def test_table_empty_cell(self):
        """
        Empty cells need to have a space in them, see <https://jira.atlassian.com/browse/JRASERVER-70048>.
        """
        markdown = """\
| A | B | C |
|-----------|
| 1 |   | 3 |
"""
        expected = """\
||A||B||C||
|1| |3|

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
