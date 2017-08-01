import unittest
import mistletoe.block_token as token
import mistletoe.ast_renderer as renderer

class TestASTRenderer(unittest.TestCase):
    def test(self):
        d = token.Document(['# heading 1', '\n', 'hello\n', 'world\n'])
        output = renderer.get_ast(d)
        target = {'type': 'Document',
                  'footnotes': {},
                  'children': [{
                      'type': 'Heading',
                      'level': 1,
                      'children': [{
                          'type': 'RawText',
                          'content': 'heading 1'
                      }]
                  }, {
                      'type': 'Paragraph',
                      'children': [{
                          'type': 'RawText',
                          'content': 'hello world'
                      }]
                 }]}
        self.assertEqual(output, target)
