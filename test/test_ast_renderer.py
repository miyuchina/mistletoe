import unittest
from mistletoe import Document, ast_renderer 

class TestASTRenderer(unittest.TestCase):
    def test(self):
        self.maxDiff = None
        d = Document(['# heading 1\n', '\n', 'hello\n', 'world\n'])
        output = ast_renderer.get_ast(d)
        target = {'type': 'Document',
                  'footnotes': {},
                  'children': [{
                      'type': 'Heading',
                      'level': 1,
                      'children': [{
                          'type': 'RawText',
                          'content': 'heading 1',
                          'parent': 'Heading'
                      }],
                      'parent': 'Document'
                  }, {
                      'type': 'Paragraph',
                      'children': [{
                          'type': 'RawText',
                          'content': 'hello',
                          'parent': 'Paragraph'
                      }, {
                          'type': 'LineBreak',
                          'soft': True,
                          'content': '',
                          'parent': 'Paragraph'
                      }, {
                          'type': 'RawText',
                          'content': 'world',
                          'parent': 'Paragraph'
                      }],
                      'parent': 'Document'
                 }]}
        self.assertEqual(output, target)

    def test_footnotes(self):
        self.maxDiff = None
        d = Document(['[bar][baz]\n',
                      '\n',
                      '[baz]: spam\n'])
        target = {'type': 'Document',
                  'footnotes': {'baz': ('spam', '')},
                  'children': [{
                      'type': 'Paragraph',
                      'children': [{
                          'type': 'Link',
                          'target': 'spam',
                          'title': '',
                          'children': [{
                              'type': 'RawText',
                              'content': 'bar',
                              'parent': 'Link'
                          }],
                          'parent': 'Paragraph'
                      }],
                      'parent': 'Document'
                 }]}
        output = ast_renderer.get_ast(d)
        self.assertEqual(output, target)
