import unittest
import core.block_token as block_token
import core.leaf_token as leaf_token

class TestHeading(unittest.TestCase):
    def test_render(self):
        token = block_token.Heading('### heading 3\n')
        self.assertEqual(token.render(), '<h3>heading 3</h3>')

class TestQuote(unittest.TestCase):
    def test_render(self):
        lines = ['> line 1\n', '> line 2\n']
        token = block_token.Quote(lines)
        output = '<blockquote><p>line 1 line 2</p></blockquote>'
        self.assertEqual(token.render(), output)

    def test_inner_render(self):
        lines = ['> ## heading 2\n',
                 '> *hello* world\n',
                 '> \n',
                 '> **new** paragraph\n',
                 '> with [link](hello)\n']
        token = block_token.Quote(lines)
        output = """<blockquote>
                        <h2>heading 2</h2>
                        <p>
                            <em>hello</em> world
                        </p>
                        <p>
                            <b>new</b> paragraph with <a href="hello">
                            link</a>
                        </p>
                    </blockquote>"""
        output = ''.join([ line.strip() for line in output.split('\n') ])
        self.assertEqual(token.render(), output)

class TestBlockCode(unittest.TestCase):
    def test_render(self):
        lines = ['```sh\n', 'rm dir\n', 'mkdir test\n', '```\n']
        token = block_token.BlockCode(lines)
        output = '<pre><code class="sh">rm dir\nmkdir test\n</code></pre>'
        self.assertEqual(token.render(), output)

    def test_escape(self):
        lines = ['```html\n',
                 '<html>\n',
                 '<b>some text</b>\n',
                 '</html>\n',
                 '```\n']
        token = block_token.BlockCode(lines)
        output = '<pre><code class="html">&lt;html&gt;\n&lt;b&gt;some text&lt;/b&gt;\n&lt;/html&gt;\n</code></pre>'
        self.assertEqual(token.render(), output)

class TestBold(unittest.TestCase):
    def test_render(self):
        self.assertEqual(leaf_token.Bold('**a str**').render(), '<b>a str</b>')

    def test_escape(self):
        self.assertEqual(leaf_token.Bold('**an &**').render(), '<b>an &amp;</b>')

class TestItalic(unittest.TestCase):
    def test_render(self):
        self.assertEqual(leaf_token.Italic('*a str*').render(), '<em>a str</em>')

    def test_escape(self):
        self.assertEqual(leaf_token.Italic('*an &*').render(), '<em>an &amp;</em>')

class TestInlineCode(unittest.TestCase):
    def test_render(self):
        token = leaf_token.InlineCode('`rm dir`')
        self.assertEqual(token.render(), '<code>rm dir</code>')

    def test_escape(self):
        token = leaf_token.InlineCode('`<html></html>`')
        output = '<code>&lt;html&gt;&lt;/html&gt;</code>'
        self.assertEqual(token.render(), output)

class TestStrikethrough(unittest.TestCase):
    def test_render(self):
        token = leaf_token.Strikethrough('~~deleted text~~')
        self.assertEqual(token.render(), '<del>deleted text</del>')

    def test_escape(self):
        token = leaf_token.Strikethrough('~~deleted &~~')
        output = '<del>deleted &amp;</del>'
        self.assertEqual(token.render(), output)

class TestLink(unittest.TestCase):
    def test_render(self):
        token = leaf_token.Link('[link name](link target)')
        output = '<a href="link target">link name</a>'
        self.assertEqual(token.render(), output)

class TestParagraph(unittest.TestCase):
    def test_render(self):
        lines = ['some\n', 'continuous\n', 'lines\n']
        token = block_token.Paragraph(lines)
        output = '<p>some continuous lines</p>'
        self.assertEqual(token.render(), output)

    def test_inner_render(self):
        lines = ['some\n',
                 '**important**\n',
                 '[info](link),\n',
                 'with `code`,\n',
                 '~~deleted text~~,\n',
                 '*etc*.\n']
        token = block_token.Paragraph(lines)
        output = """<p>
                       some <b>important</b> <a href="link">info</a>
                       , with <code>code</code>
                       , <del>deleted text</del>
                       , <em>etc</em>.
                    </p>"""
        output = ''.join([ line.strip() for line in output.split('\n') ])
        self.assertEqual(token.render(), output)

class TestListItem(unittest.TestCase):
    def test_render(self):
        token = block_token.ListItem('- some text\n')
        self.assertEqual(token.render(), '<li>some text</li>')

class TestList(unittest.TestCase):
    def test_render(self):
        token = block_token.List()
        token.add(block_token.ListItem('- item 1\n'))
        token.add(block_token.ListItem('- item 2\n'))
        sublist = block_token.List()
        sublist.add(block_token.ListItem('    - nested item 1\n'))
        sublist.add(block_token.ListItem('    - nested item 2\n'))
        subsublist = block_token.List()
        subsublist.add(block_token.ListItem('        - **further** nested item\n'))
        sublist.add(subsublist)
        sublist.add(block_token.ListItem('    - nested item 3\n'))
        token.add(sublist)
        token.add(block_token.ListItem('- item 3\n'))

        output = """<ul>
                        <li>item 1</li>
                        <li>item 2</li>
                        <ul>
                            <li>nested item 1</li>
                            <li>nested item 2</li>
                            <ul>
                                <li><b>further</b> nested item</li>
                            </ul>
                            <li>nested item 3</li>
                        </ul>
                        <li>item 3</li>
                    </ul>"""
        output = ''.join([ line.strip() for line in output.split('\n') ])
        self.assertEqual(token.render(), output)

class TestSeparator(unittest.TestCase):
    def test_render(self):
        self.assertEqual(block_token.Separator('---\n').render(), '<hr>')

class TestRawText(unittest.TestCase):
    def test_render(self):
        self.assertEqual(leaf_token.RawText('some text').render(), 'some text')

    def test_escape(self):
        self.assertEqual(leaf_token.RawText('an &').render(), 'an &amp;')

