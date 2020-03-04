from textwrap import dedent
import unittest

from mistletoe import Document
from mistletoe.utils import traverse


class TestTraverse(unittest.TestCase):
    def test_a(self):
        doc = Document(
            dedent(
                """\
            a **b**

            c [*d*](link)
            """
            )
        )
        tree = [
            (
                t.node.__class__.__name__,
                t.parent.__class__.__name__ if t.parent else None,
                t.depth
            )
            for t in traverse(doc, include_source=True)
        ]
        self.assertEqual(
            tree,
            [
                ('Document', None, 0),
                ('Paragraph', 'Document', 1),
                ('Paragraph', 'Document', 1),
                ('RawText', 'Paragraph', 2),
                ('Strong', 'Paragraph', 2),
                ('RawText', 'Paragraph', 2),
                ('Link', 'Paragraph', 2),
                ('RawText', 'Strong', 3),
                ('Emphasis', 'Link', 3),
                ('RawText', 'Emphasis', 4),
            ]
        )
