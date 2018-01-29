import unittest
from mistletoe import Document, ast_renderer 

class TestASTRenderer(unittest.TestCase):
    def test(self):
        self.maxDiff = None
        d = Document(['# heading 1', '\n', 'hello\n', 'world\n'])
        output = ast_renderer.get_ast(d)
        target = {'type': 'Document',
                  'footnotes': {},
                  'children': [{
                      'type': 'Heading',
                      'level': 1,
                      'children': [{
                          'type': 'RawText',
                          'content': 'heading 1',
                          'escape': True
                      }]
                  }, {
                      'type': 'Paragraph',
                      'children': [{
                          'type': 'RawText',
                          'content': 'hello\nworld\n',
                          'escape': True
                      }]
                 }]}
        self.assertEqual(output, target)

    def test_footnotes(self):
        self.maxDiff = None
        d = Document(['[bar][baz]\n',
                      '\n',
                      '[baz]: spam\n'])
        target = {'type': 'Document',
                  'footnotes': {'baz': 'spam'},
                  'children': [{
                      'type': 'Paragraph',
                      'children': [{
                          'type': 'FootnoteLink',
                          'target': {
                              'type': 'FootnoteAnchor',
                              'key': 'baz'
                          },
                          'children': [{
                              'type': 'RawText',
                              'content': 'bar',
                              'escape': True
                          }]
                      }, {
                          'type': 'RawText',
                          'content': '\n',
                          'escape': True }
                      ]
                 }]}
        output = ast_renderer.get_ast(d)
        self.assertEqual(output, target)
