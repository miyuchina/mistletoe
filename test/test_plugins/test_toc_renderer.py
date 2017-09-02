from unittest import TestCase, mock
from mistletoe.block_token import Document, Heading
from plugins.toc_renderer import TOCRenderer

class TestTOCRenderer(TestCase):
    def test_parse_rendered_heading(self):
        rendered_heading = '<h3>some <em>text</em></h3>\n'
        content = TOCRenderer.parse_rendered_heading(rendered_heading)
        self.assertEqual(content, 'some text')

    def test_render_heading(self):
        renderer = TOCRenderer()
        token = Heading(['### some *text*\n'])
        rendered_heading = renderer.render_heading(token)
        self.assertEqual(renderer._headings[0], (3, 'some text'))

    def test_depth(self):
        renderer = TOCRenderer(depth=3)
        token = Document(['# title\n', '## heading\n', '#### heading\n'])
        renderer.render(token)
        self.assertEqual(renderer._headings, [(2, 'heading')])

    def test_omit_title(self):
        renderer = TOCRenderer(omit_title=True)
        token = Document(['# title\n', '\n', '## heading\n'])
        renderer.render(token)
        self.assertEqual(renderer._headings, [(2, 'heading')])

    def test_filter_conditions(self):
        import re
        filter_conds = [lambda x: re.match(r'heading', x),
                        lambda x: re.match(r'foo', x)]
        renderer = TOCRenderer(filter_conds=filter_conds)
        token = Document(['# title\n',
                          '\n',
                          '## heading\n',
                          '\n',
                          '#### not heading\n'])
        renderer.render(token)
        self.assertEqual(renderer._headings, [(4, 'not heading')])

    @mock.patch('mistletoe.block_token.List')
    def test_get_toc(self, MockList):
        headings = [(1, 'heading 1'),
                    (2, 'subheading 1'),
                    (2, 'subheading 2'),
                    (3, 'subsubheading 1'),
                    (2, 'subheading 3'),
                    (1, 'heading 2')]
        renderer = TOCRenderer(omit_title=False)
        renderer._headings = headings
        toc = renderer.toc
        MockList.assert_called_with(['- heading 1\n',
                                     '    - subheading 1\n',
                                     '    - subheading 2\n',
                                     '        - subsubheading 1\n',
                                     '    - subheading 3\n',
                                     '- heading 2\n'])
