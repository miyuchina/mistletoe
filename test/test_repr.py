import unittest

from mistletoe import Document
from mistletoe import block_token


class TestRepr(unittest.TestCase):
    def _check_repr_matches(self, token, expected_match):
        expected_match = "<mistletoe.{} at 0x".format(expected_match)
        output = repr(token)[:len(expected_match)]
        self.assertEqual(output, expected_match)

    # Block tokens

    def test_document(self):
        doc = Document("# Foo")
        self._check_repr_matches(doc, "block_token.Document with 1 child line_number=1")

    def test_heading(self):
        doc = Document("# Foo")
        self._check_repr_matches(doc.children[0], "block_token.Heading with 1 child line_number=1 level=1")
        self._check_repr_matches(doc.children[0].children[0], "span_token.RawText content='Foo'")

    def test_subheading(self):
        doc = Document("# Foo\n## Bar")
        self._check_repr_matches(doc.children[1], "block_token.Heading with 1 child line_number=2 level=2")
        self._check_repr_matches(doc.children[1].children[0], "span_token.RawText content='Bar'")

    def test_quote(self):
        doc = Document("> Foo")
        self._check_repr_matches(doc.children[0], "block_token.Quote with 1 child line_number=1")

    def test_paragraph(self):
        doc = Document("Foo")
        self._check_repr_matches(doc.children[0], "block_token.Paragraph with 1 child line_number=1")

    def test_blockcode(self):
        doc = Document("Foo\n\n\tBar\n\nBaz")
        self._check_repr_matches(doc.children[1], "block_token.BlockCode with 1 child line_number=3 language=''")

    def test_codefence(self):
        doc = Document("""```python\nprint("Hello, World!"\n```""")
        self._check_repr_matches(doc.children[0], "block_token.CodeFence with 1 child line_number=1 language='python'")

    def test_unordered_list(self):
        doc = Document("* Foo\n* Bar\n* Baz")
        self._check_repr_matches(doc.children[0], "block_token.List with 3 children line_number=1 loose=False start=None")
        self._check_repr_matches(doc.children[0].children[0], "block_token.ListItem with 1 child line_number=1 leader='*' indentation=0 prepend=2 loose=False")

    def test_ordered_list(self):
        doc = Document("1. Foo\n2. Bar\n3. Baz")
        self._check_repr_matches(doc.children[0], "block_token.List with 3 children line_number=1 loose=False start=1")
        self._check_repr_matches(doc.children[0].children[0], "block_token.ListItem with 1 child line_number=1 leader='1.' indentation=0 prepend=3 loose=False")

    def test_table(self):
        doc = Document("| Foo | Bar | Baz |\n|:--- |:---:| ---:|\n| Foo | Bar | Baz |\n")
        self._check_repr_matches(doc.children[0], "block_token.Table with 1 child line_number=1 column_align=[None, 0, 1]")
        self._check_repr_matches(doc.children[0].children[0], "block_token.TableRow with 3 children line_number=3 row_align=[None, 0, 1]")
        self._check_repr_matches(doc.children[0].children[0].children[0], "block_token.TableCell with 1 child line_number=3 align=None")

    def test_thematicbreak(self):
        doc = Document("Foo\n\n---\n\nBar\n")
        self._check_repr_matches(doc.children[1], "block_token.ThematicBreak line_number=3")

    # No test for ``Footnote``

    def test_htmlblock(self):
        try:
            block_token.add_token(block_token.HtmlBlock)
            doc = Document("<pre>\nFoo\n</pre>\n")
        finally:
            block_token.reset_tokens()
        self._check_repr_matches(doc.children[0], "block_token.HtmlBlock with 1 child line_number=1")
        self._check_repr_matches(doc.children[0].children[0], "span_token.RawText content='<pre>\\nFoo\\n</pre>'")

    # Span tokens

    def test_strong(self):
        doc = Document("**foo**\n")
        self._check_repr_matches(doc.children[0].children[0], "span_token.Strong with 1 child")

    def test_emphasis(self):
        doc = Document("*foo*\n")
        self._check_repr_matches(doc.children[0].children[0], "span_token.Emphasis with 1 child")

    def test_inlinecode(self):
        doc = Document("`foo`\n")
        self._check_repr_matches(doc.children[0].children[0], "span_token.InlineCode with 1 child")

    def test_strikethrough(self):
        doc = Document("~~foo~~\n")
        self._check_repr_matches(doc.children[0].children[0], "span_token.Strikethrough with 1 child")

    def test_image(self):
        doc = Document("""![Foo](http://www.example.org/ "bar")\n""")
        self._check_repr_matches(doc.children[0].children[0], "span_token.Image with 1 child src='http://www.example.org/' title='bar'")

    def test_link(self):
        doc = Document("[Foo](http://www.example.org/)\n")
        self._check_repr_matches(doc.children[0].children[0], "span_token.Link with 1 child target='http://www.example.org/' title=''")

    def test_autolink(self):
        doc = Document("Foo <http://www.example.org/>\n")
        self._check_repr_matches(doc.children[0].children[1], "span_token.AutoLink with 1 child target='http://www.example.org/' mailto=False")

    def test_escapesequence(self):
        doc = Document("\\*\n")
        self._check_repr_matches(doc.children[0].children[0], "span_token.EscapeSequence with 1 child")

    def test_soft_linebreak(self):
        doc = Document("Foo\nBar\n")
        self._check_repr_matches(doc.children[0].children[1], "span_token.LineBreak content='' soft=True")

    def test_hard_linebreak(self):
        doc = Document("Foo\\\nBar\n")
        self._check_repr_matches(doc.children[0].children[1], "span_token.LineBreak content='\\\\' soft=False")

    def test_rawtext(self):
        doc = Document("Foo\n")
        self._check_repr_matches(doc.children[0].children[0], "span_token.RawText content='Foo'")
