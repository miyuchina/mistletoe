import unittest
import core.block_token as block_token
import core.leaf_token as leaf_token
import lib.html_renderer as renderer

class TestHTMLRenderer(unittest.TestCase):
    def test_tagify(self):
        output = renderer.tagify('p', 'some text')
        target = '<p>some text</p>'
        self.assertEqual(output, target)

    def test_tagify_attrs(self):
        output = renderer.tagify_attrs('a', { 'href': 'hi' }, 'some text')
        target = '<a href="hi">some text</a>'
        self.assertEqual(output, target)

    def test_bold(self):
        output = renderer.render(leaf_token.Bold('**some text**'))
        self.assertEqual(output, '<b>some text</b>')

    def test_italic(self):
        output = renderer.render(leaf_token.Italic('*some text*'))
        self.assertEqual(output, '<em>some text</em>')

    def test_inline_code(self):
        output = renderer.render(leaf_token.InlineCode('`some code`'))
        self.assertEqual(output, '<code>some code</code>')

    def test_strikethrough(self):
        output = renderer.render(leaf_token.Strikethrough('~~text~~'))
        self.assertEqual(output, '<del>text</del>')

    def test_link(self):
        output = renderer.render(leaf_token.Link('[name](target)'))
        self.assertEqual(output, '<a href="target">name</a>')

    def test_raw_text(self):
        output = renderer.render(leaf_token.RawText('some text'))
        self.assertEqual(output, 'some text')

    def test_heading(self):
        output = renderer.render(block_token.Heading('# heading 1'))
        self.assertEqual(output, '<h1>heading 1</h1>')

    def test_quote(self):
        lines = ['> # heading 1\n',
                 '> a paragraph\n',
                 '> that spans\n',
                 '> a few lines.\n']
        output = renderer.render(block_token.Quote(lines))
        target = ('<blockquote>'
               +      '<h1>heading 1</h1>'
               +      '<p>a paragraph that spans a few lines.</p>'
               +  '</blockquote>')
        self.assertEqual(output, target)

    def test_paragraph(self):
        lines = ['a paragraph\n', 'that spans\n', 'a few lines.\n']
        output = renderer.render(block_token.Paragraph(lines))
        target = '<p>a paragraph that spans a few lines.</p>'
        self.assertEqual(output, target)

    def test_block_code(self):
        lines = ['```sh\n',
                 'rm -rf *\n',
                 'mkdir test\n',
                 '```\n']
        output = renderer.render(block_token.BlockCode(lines))
        target = ('<pre>'
               +      '<code class="sh">'
               +          'rm -rf *\n'
               +          'mkdir test\n'
               +      '</code>'
               +  '</pre>')
        self.assertEqual(output, target)

    def test_list_item(self):
        output = renderer.render(block_token.ListItem('- some text\n'))
        target = '<li>some text</li>'

    def test_list(self):
        token = block_token.List()
        token.add(block_token.ListItem('- item 1\n'))
        token.add(block_token.ListItem('- item 2\n'))
        sublist = block_token.List()
        sublist.add(block_token.ListItem('    - nested item 1\n'))
        sublist.add(block_token.ListItem('    - nested item 2\n'))
        token.add(sublist)
        token.add(block_token.ListItem('- item 3\n'))
        target = ('<ul>'
               +      '<li>item 1</li>'
               +      '<li>item 2</li>'
               +      '<ul>'
               +          '<li>nested item 1</li>'
               +          '<li>nested item 2</li>'
               +      '</ul>'
               +      '<li>item 3</li>'
               +  '</ul>')
        self.assertEqual(renderer.render(token), target)

    def test_separator(self):
        output = renderer.render(block_token.Separator('---\n'))
        target = '<hr>'
        self.assertEqual(output, target)

    def test_document(self):
        output = renderer.render(block_token.Document(['some text\n']))
        target = '<html><body><p>some text</p></body></html>'
        self.assertEqual(output, target)

