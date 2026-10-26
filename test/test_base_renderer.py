from unittest import TestCase

from mistletoe import Document
from mistletoe.base_renderer import BaseRenderer


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
