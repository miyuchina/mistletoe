import unittest

from mistletoe import Document
from mistletoe.contrib.pygments_renderer import PygmentsRenderer
from parameterized import parameterized
from pygments.util import ClassNotFound


class TestPygmentsRenderer(unittest.TestCase):
    @parameterized.expand([(True,), (False,)])
    def test_render_no_language(self, fail_on_unsupported_language: bool):
        renderer = PygmentsRenderer(fail_on_unsupported_language=fail_on_unsupported_language)
        token = Document(['```\n', 'no language\n', '```\n'])
        output = renderer.render(token)
        expected = (
            '<div class="highlight" style="background: #f8f8f8"><pre style="line-height: 125%;">'
            '<span></span>no language\n</pre></div>\n\n'
        )
        self.assertEqual(output, expected)

    def test_render_known_language(self):
        renderer = PygmentsRenderer()
        token = Document(['```python\n', '# python language\n', '```\n'])
        output = renderer.render(token)
        expected = (
            '<div class="highlight" style="background: #f8f8f8"><pre style="line-height: 125%;">'
            '<span></span><span style="color: #3D7B7B; font-style: italic"># python language</span>\n'
            '</pre></div>\n\n'
        )
        self.assertEqual(output, expected)

    def test_render_unknown_language(self):
        renderer = PygmentsRenderer()
        token = Document(['```foobar\n', 'unknown language\n', '```\n'])
        output = renderer.render(token)
        expected = (
            '<div class="highlight" style="background: #f8f8f8"><pre style="line-height: 125%;">'
            '<span></span>unknown language\n</pre></div>\n\n'
        )
        self.assertEqual(output, expected)

    def test_render_fail_on_unsupported_language(self):
        renderer = PygmentsRenderer(fail_on_unsupported_language=True)
        token = Document(['```foobar\n', 'unknown language\n', '```\n'])
        with self.assertRaises(ClassNotFound):
            renderer.render(token)
