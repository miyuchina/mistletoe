import pytest

from mistletoe import Document
from mistletoe.contrib.pygments_renderer import PygmentsRenderer
from pygments.util import ClassNotFound


class TestPygmentsRenderer:
    @pytest.mark.parametrize('fail_on_unsupported_language', [True, False],
                             ids=['strict', 'permissive'])
    def test_render_no_language(self, fail_on_unsupported_language: bool):
        renderer = PygmentsRenderer(fail_on_unsupported_language=fail_on_unsupported_language)
        token = Document(['```\n', 'no language\n', '```\n'])
        output = renderer.render(token)
        expected = (
            '<div class="highlight" style="background: #f8f8f8"><pre style="line-height: 125%;">'
            '<span></span>no language\n</pre></div>\n\n'
        )
        assert output == expected

    def test_render_known_language(self):
        renderer = PygmentsRenderer()
        token = Document(['```python\n', '# python language\n', '```\n'])
        output = renderer.render(token)
        expected = (
            '<div class="highlight" style="background: #f8f8f8"><pre style="line-height: 125%;">'
            '<span></span><span style="color: #3D7B7B; font-style: italic"># python language</span>\n'
            '</pre></div>\n\n'
        )
        assert output == expected

    def test_render_unknown_language(self):
        renderer = PygmentsRenderer()
        token = Document(['```foobar\n', 'unknown language\n', '```\n'])
        output = renderer.render(token)
        expected = (
            '<div class="highlight" style="background: #f8f8f8"><pre style="line-height: 125%;">'
            '<span></span>unknown language\n</pre></div>\n\n'
        )
        assert output == expected

    def test_render_fail_on_unsupported_language(self):
        renderer = PygmentsRenderer(fail_on_unsupported_language=True)
        token = Document(['```foobar\n', 'unknown language\n', '```\n'])
        with pytest.raises(ClassNotFound):
            renderer.render(token)
