from textwrap import dedent
import unittest

from mistletoe import Document
from mistletoe.span_token import Strong
from mistletoe.utils import traverse


class TestTraverse(unittest.TestCase):
    def test(self):
        doc = Document("a **b** c **d**")
        filtered = [t.node.__class__.__name__ for t in traverse(doc)]
        self.assertEqual(
            filtered,
            [
                "Paragraph",
                "RawText",
                "Strong",
                "RawText",
                "Strong",
                "RawText",
                "RawText",
            ],
        )

    def test_with_included_source(self):
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

    def test_with_class_filter(self):
        doc = Document("a **b** c **d**")
        filtered = [t.node.__class__.__name__ for t in traverse(doc, klass=Strong)]
        self.assertEqual(filtered, ["Strong", "Strong"])

    def test_with_included_source_and_class_filter(self):
        doc = Document("a **b** c **d**")
        filtered = [
            t.node.__class__.__name__
            for t in traverse(doc, include_source=True, klass=Strong)
        ]
        self.assertEqual(filtered, ["Strong", "Strong"])

    def test_with_depth_limit(self):
        doc = Document("a **b** c **d**")

        # Zero depth with root not included yields no nodes.
        filtered = [t.node.__class__.__name__ for t in traverse(doc, depth=0)]
        self.assertEqual(filtered, [])

        # Zero depth with root included yields the root node.
        filtered = [
            t.node.__class__.__name__
            for t in traverse(doc, depth=0, include_source=True)
        ]
        self.assertEqual(filtered, ["Document"])

        # Depth=1 correctly returns the single node at that level.
        filtered = [t.node.__class__.__name__ for t in traverse(doc, depth=1)]
        self.assertEqual(filtered, ["Paragraph"])

        # Depth=2 returns the correct nodes.
        filtered = [t.node.__class__.__name__ for t in traverse(doc, depth=2)]
        self.assertEqual(
            filtered, ["Paragraph", "RawText", "Strong", "RawText", "Strong"]
        )

        # Depth=3 returns the correct nodes (all nodes in the tree).
        filtered = [t.node.__class__.__name__ for t in traverse(doc, depth=3)]
        self.assertEqual(
            filtered,
            [
                "Paragraph",
                "RawText",
                "Strong",
                "RawText",
                "Strong",
                "RawText",
                "RawText",
            ],
        )

        # Verify there are no additional nodes at depth=4.
        filtered = [t.node.__class__.__name__ for t in traverse(doc, depth=4)]
        self.assertEqual(
            filtered,
            [
                "Paragraph",
                "RawText",
                "Strong",
                "RawText",
                "Strong",
                "RawText",
                "RawText",
            ],
        )
