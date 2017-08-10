import unittest
import test.helpers as helpers
from mistletoe.block_token import Heading, List
from plugins.toc_renderer import TOCRenderer

class TestTOCRenderer(unittest.TestCase):
    def test_store_rendered_heading(self):
        renderer = TOCRenderer()
        rendered_heading = '<h3>some <em>text</em></h3>\n'
        renderer.store_rendered_heading(rendered_heading)
        self.assertEqual(renderer.headings[0], (3, 'some text'))

    def test_render_heading(self):
        renderer = TOCRenderer()
        token = Heading(['### some *text*\n'])
        rendered_heading = renderer.render_heading(token, {})
        self.assertEqual(renderer.headings[0], (3, 'some text'))

    def test_get_toc(self):
        headings = [(1, 'heading 1'),
                    (2, 'subheading 1'),
                    (2, 'subheading 2'),
                    (3, 'subsubheading 1'),
                    (2, 'subheading 3'),
                    (1, 'heading 2')]
        renderer = TOCRenderer()
        renderer.headings = headings
        toc = List(['- heading 1\n',
                    '    - subheading 1\n',
                    '    - subheading 2\n',
                    '        - subsubheading 1\n',
                    '    - subheading 3\n',
                    '- heading 2\n'])
        helpers.check_equal(self, renderer.toc, toc)
