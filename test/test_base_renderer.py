import pytest

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


class TestBaseRenderer:
    @pytest.mark.parametrize('markdown', [case[1] for case in LINE_BREAKS],
                             ids=[case[0] for case in LINE_BREAKS])
    def test_line_break_requires_override(self, markdown):
        with BaseRenderer() as renderer:
            with pytest.raises(NotImplementedError, match='render_line_break'):
                renderer.render(Document(markdown))

    @pytest.mark.parametrize('markdown, expected', [case[1:] for case in LINE_BREAKS],
                             ids=[case[0] for case in LINE_BREAKS])
    def test_line_break_override(self, markdown, expected):
        class TextRenderer(BaseRenderer):
            def render_line_break(self, token):
                return '\n'

        with TextRenderer() as renderer:
            assert renderer.render(Document(markdown)) == expected
