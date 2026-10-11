from unittest import TestCase

from parameterized import parameterized

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
    @parameterized.expand(LINE_BREAKS)
    def test_line_break_requires_override(self, name, markdown, expected):
        with BaseRenderer() as renderer:
            with self.assertRaisesRegex(NotImplementedError, 'render_line_break'):
                renderer.render(Document(markdown))

    @parameterized.expand(LINE_BREAKS)
    def test_line_break_override(self, name, markdown, expected):
        class TextRenderer(BaseRenderer):
            def render_line_break(self, token):
                return '\n'

        with TextRenderer() as renderer:
            self.assertEqual(renderer.render(Document(markdown)), expected)
