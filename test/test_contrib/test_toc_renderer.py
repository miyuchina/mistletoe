from unittest import TestCase
from mistletoe import block_token
from mistletoe.block_token import Document, Heading
from mistletoe.contrib.toc_renderer import TocRenderer


class TestTocRenderer(TestCase):
    def test_parse_rendered_heading(self):
        rendered_heading = '<h3>some <em>text</em></h3>'
        content = TocRenderer.parse_rendered_heading(rendered_heading)
        self.assertEqual(content, 'some text')

    def test_render_heading(self):
        renderer = TocRenderer()
        Heading.start('### some *text*\n')
        token = Heading(Heading.read(iter(['foo'])))
        renderer.render_heading(token)
        self.assertEqual(renderer._headings[0], (3, 'some text'))

    def test_depth(self):
        renderer = TocRenderer(depth=3)
        token = Document(['# title\n', '## heading\n', '#### heading\n'])
        renderer.render(token)
        self.assertEqual(renderer._headings, [(2, 'heading')])

    def test_omit_title(self):
        renderer = TocRenderer(omit_title=True)
        token = Document(['# title\n', '\n', '## heading\n'])
        renderer.render(token)
        self.assertEqual(renderer._headings, [(2, 'heading')])

    def test_filter_conditions(self):
        import re
        filter_conds = [lambda x: re.match(r'heading', x),
                        lambda x: re.match(r'foo', x)]
        renderer = TocRenderer(filter_conds=filter_conds)
        token = Document(['# title\n',
                          '\n',
                          '## heading\n',
                          '\n',
                          '#### not heading\n'])
        renderer.render(token)
        self.assertEqual(renderer._headings, [(4, 'not heading')])

    def test_get_toc(self):
        headings = [(1, 'heading 1'),
                    (2, 'subheading 1'),
                    (2, 'subheading 2'),
                    (3, 'subsubheading 1'),
                    (2, 'subheading 3'),
                    (1, 'heading 2')]
        renderer = TocRenderer(omit_title=False)
        renderer._headings = headings
        toc = renderer.toc
        self.assertIsInstance(toc, block_token.List)
        # for now, we check at least the most nested heading
        # (hierarchy: `List -> ListItem -> {Paragraph -> RawText.content | List -> ...}`):
        heading_item = toc.children[0].children[1].children[1].children[1].children[0]
        self.assertIsInstance(heading_item, block_token.ListItem)
        self.assertEqual(heading_item.children[0].children[0].content, 'subsubheading 1')
