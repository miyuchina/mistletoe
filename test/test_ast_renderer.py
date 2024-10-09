import unittest
from mistletoe import Document, ast_renderer


class TestAstRenderer(unittest.TestCase):
    def test(self):
        self.maxDiff = None
        d = Document([
            '# heading 1\n',
            '\n',
            'hello\n',
            'world\n',
        ])
        output = ast_renderer.get_ast(d)
        expected = {'type': 'Document',
                  'footnotes': {},
                  'line_number': 1,
                  'children': [{
                      'type': 'Heading',
                      'level': 1,
                      'line_number': 1,
                      'children': [{
                          'type': 'RawText',
                          'content': 'heading 1'
                      }]
                  }, {
                      'type': 'Paragraph',
                      'line_number': 3,
                      'children': [{
                          'type': 'RawText',
                          'content': 'hello'
                      }, {
                          'type': 'LineBreak',
                          'soft': True,
                          'content': ''
                      }, {
                          'type': 'RawText',
                          'content': 'world'
                      }]
                  }]}
        self.assertEqual(output, expected)

    def test_footnotes(self):
        self.maxDiff = None
        d = Document([
            '[bar][baz]\n',
            '\n',
            '[baz]: spam\n',
        ])
        expected = {'type': 'Document',
                  'footnotes': {'baz': ('spam', '')},
                  'line_number': 1,
                  'children': [{
                      'type': 'Paragraph',
                      'line_number': 1,
                      'children': [{
                          'type': 'Link',
                          'target': 'spam',
                          'title': '',
                          'children': [{
                              'type': 'RawText',
                              'content': 'bar'
                          }]
                      }]
                  }]}
        output = ast_renderer.get_ast(d)
        self.assertEqual(output, expected)

    def test_table(self):
        self.maxDiff = None
        d = Document([
            "| A   | B   |\n",
            "| --- | --- |\n",
            "| 1   | 2   |\n",
        ])
        expected = {
            "type": "Document",
            "footnotes": {},
            'line_number': 1,
            "children": [{
                "type": "Table",
                "column_align": [None, None],
                'line_number': 1,
                "header": {
                    "type": "TableRow",
                    "row_align": [None, None],
                    'line_number': 1,
                    "children": [{
                        "type": "TableCell",
                        "align": None,
                        'line_number': 1,
                        "children": [{
                            "type": "RawText",
                            "content": "A",
                        }]}, {
                        "type": "TableCell",
                        "align": None,
                        'line_number': 1,
                        "children": [{
                            "type": "RawText",
                            "content": "B",
                        }]
                    }],
                },
                "children": [{
                    "type": "TableRow",
                    "row_align": [None, None],
                    'line_number': 3,
                    "children": [{
                        "type": "TableCell",
                        "align": None,
                        'line_number': 3,
                        "children": [{
                            "type": "RawText",
                            "content": "1",
                        }]}, {
                        "type": "TableCell",
                        "align": None,
                        'line_number': 3,
                        "children": [{
                            "type": "RawText",
                            "content": "2",
                        }]
                    }],
                }],
            }],
        }
        output = ast_renderer.get_ast(d)
        self.assertEqual(output, expected)
