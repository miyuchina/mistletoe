import unittest

from mistletoe import Document
from mistletoe import block_token


class TestRepr(unittest.TestCase):
    def check_repr_prefix(self, token, expected_prefix):
        output = repr(token)[:len(expected_prefix)]
        self.assertEqual(output, expected_prefix)

    # Block tokens

    def test_document(self):
        doc = Document("# Foo")
        self.check_repr_prefix(doc, "<mistletoe.block_token.Document with 1 child at 0x")

    def test_heading(self):
        doc = Document("# Foo")
        self.check_repr_prefix(doc.children[0], "<mistletoe.block_token.Heading with 1 child content='Foo' level=1 at 0x")

    def test_subheading(self):
        doc = Document("# Foo\n## Bar")
        self.check_repr_prefix(doc.children[1], "<mistletoe.block_token.Heading with 1 child content='Bar' level=2 at 0x")

    def test_quote(self):
        doc = Document("> Foo")
        self.check_repr_prefix(doc.children[0], "<mistletoe.block_token.Quote with 1 child at 0x")

    def test_paragraph(self):
        doc = Document("Foo")
        self.check_repr_prefix(doc.children[0], "<mistletoe.block_token.Paragraph with 1 child at 0x")

    def test_blockcode(self):
        doc = Document("Foo\n\n\tBar\n\nBaz")
        self.check_repr_prefix(doc.children[1], "<mistletoe.block_token.BlockCode with 1 child language='' at 0x")

    def test_codefence(self):
        doc = Document("""```python\nprint("Hello, World!"\n```""")
        self.check_repr_prefix(doc.children[0], "<mistletoe.block_token.CodeFence with 1 child language='python' at 0x")

    def test_unordered_list(self):
        doc = Document("* Foo\n* Bar\n* Baz")
        self.check_repr_prefix(doc.children[0], "<mistletoe.block_token.List with 3 children loose=False start=None at 0x")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.block_token.ListItem with 1 child leader='*' prepend=2 loose=False at 0x")

    def test_ordered_list(self):
        doc = Document("1. Foo\n2. Bar\n3. Baz")
        self.check_repr_prefix(doc.children[0], "<mistletoe.block_token.List with 3 children loose=False start=1 at 0x")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.block_token.ListItem with 1 child leader='1.' prepend=3 loose=False at 0x")

    def test_table(self):
        doc = Document("| Foo | Bar | Baz |\n|:--- |:---:| ---:|\n| Foo | Bar | Baz |\n")
        self.check_repr_prefix(doc.children[0], "<mistletoe.block_token.Table with 1 child column_align=[None, 0, 1] at 0x")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.block_token.TableRow with 3 children row_align=[None, 0, 1] at 0x")
        self.check_repr_prefix(doc.children[0].children[0].children[0], "<mistletoe.block_token.TableCell with 1 child align=None at 0x")

    def test_thematicbreak(self):
        doc = Document("Foo\n\n---\n\nBar\n")
        self.check_repr_prefix(doc.children[1], "<mistletoe.block_token.ThematicBreak at 0x")

    # No test for ``Footnote``

    def test_htmlblock(self):
        token = block_token.HTMLBlock("<pre>\nFoo\n</pre>\n")
        self.check_repr_prefix(token, "<mistletoe.block_token.HTMLBlock content='<pre>\\nFoo\\n</pre>' at 0x")

    # Span tokens

    def test_strong(self):
        doc = Document("**foo**\n")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.span_token.Strong with 1 child at 0x")

    def test_emphasis(self):
        doc = Document("*foo*\n")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.span_token.Emphasis with 1 child at 0x")

    def test_inlinecode(self):
        doc = Document("`foo`\n")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.span_token.InlineCode with 1 child at 0x")

    def test_strikethrough(self):
        doc = Document("~~~foo~~~\n")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.span_token.Strikethrough with 1 child at 0x")

    def test_image(self):
        doc = Document("""![Foo](http://www.example.org/ "bar")\n""")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.span_token.Image with 1 child src='http://www.example.org/' title='bar' at 0x")

    def test_link(self):
        doc = Document("[Foo](http://www.example.org/)\n")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.span_token.Link with 1 child target='http://www.example.org/' title='' at 0x")

    def test_autolink(self):
        doc = Document("Foo <http://www.example.org/>\n")
        self.check_repr_prefix(doc.children[0].children[1], "<mistletoe.span_token.AutoLink with 1 child target='http://www.example.org/' mailto=False at 0x")

    def test_escapesequence(self):
        doc = Document("\\*\n")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.span_token.EscapeSequence with 1 child at 0x")

    def test_soft_linebreak(self):
        doc = Document("Foo\nBar\n")
        self.check_repr_prefix(doc.children[0].children[1], "<mistletoe.span_token.LineBreak content='' soft=True at 0x")

    def test_hard_linebreak(self):
        doc = Document("Foo\\\nBar\n")
        self.check_repr_prefix(doc.children[0].children[1], "<mistletoe.span_token.LineBreak content='' soft=False at 0x")

    def test_rawtext(self):
        doc = Document("Foo\n")
        self.check_repr_prefix(doc.children[0].children[0], "<mistletoe.span_token.RawText content='Foo' at 0x")
