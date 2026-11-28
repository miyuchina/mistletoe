from unittest import TestCase

from mistletoe import Document
from mistletoe.base_renderer import BaseRenderer
from mistletoe.html_renderer import HtmlRenderer
from mistletoe.latex_renderer import LaTeXRenderer
from mistletoe.markdown_renderer import MarkdownRenderer


LINE_BREAKS = [
    ('soft_lf', 'first\nsecond', 'first\nsecond'),
    ('soft_crlf', 'first\r\nsecond', 'first\r\nsecond'),
    ('spaces_lf', 'first  \nsecond', 'first\nsecond'),
    ('spaces_crlf', 'first  \r\nsecond', 'first  \r\nsecond'),
    ('backslash_lf', 'first\\\nsecond', 'first\nsecond'),
    ('backslash_crlf', 'first\\\r\nsecond', 'first\\\r\nsecond'),
]


class TestBaseRenderer(TestCase):
    def test_line_break_requires_override(self):
        for name, markdown, _expected in LINE_BREAKS:
            with self.subTest(name=name):
                with BaseRenderer() as renderer:
                    with self.assertRaisesRegex(NotImplementedError, 'render_line_break'):
                        renderer.render(Document(markdown))

    def test_line_break_override(self):
        class TextRenderer(BaseRenderer):
            def render_line_break(self, token):
                return '\n'

        for name, markdown, expected in LINE_BREAKS:
            with self.subTest(name=name):
                with TextRenderer() as renderer:
                    self.assertEqual(renderer.render(Document(markdown)), expected)

    def test_render_with_markdown_renderer_active(self):
        # Regression test for #318: MarkdownRenderer registers BlankLine
        # and LinkReferenceDefinitionBlock as global parse tokens, so a
        # Document created while it is active contains them. Other
        # renderers must not crash with KeyError on those tokens.
        with HtmlRenderer() as html, MarkdownRenderer() as md:
            self.assertEqual(html.render(Document('a\n\nb')),
                             '<p>a</p>\n\n<p>b</p>\n')
            self.assertEqual(md.render(Document('a\n\nb')), 'a\n\nb\n')

        with LaTeXRenderer() as latex, MarkdownRenderer() as md:
            self.assertIn('\\href{https://example.com}{a}',
                          latex.render(Document('[a]: https://example.com\n\n[a]\n')))
            self.assertEqual(md.render(Document('[a]: https://example.com\n\n[a]\n')),
                             '[a]: https://example.com\n\n[a]\n')
