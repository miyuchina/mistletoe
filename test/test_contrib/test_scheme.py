from unittest import TestCase

import mistletoe
from mistletoe.block_token import Document
from mistletoe.contrib.scheme import Program, Scheme


class TestScheme(TestCase):
    def test_render(self):
        with Scheme() as renderer:
            prog = [
                "(define x (* 2 21))",
                "x",
            ]
            result = renderer.render(Program(prog))
            self.assertEqual(result, 42)


class TestSchemeDocument(TestCase):
    """The Scheme renderer used to raise a bare KeyError on a Document,
    so it could not be used from the command line interface."""

    def test_render_document(self):
        with Scheme() as renderer:
            doc = Document(["(define x (* 2 21))\n", "x\n"])
            self.assertEqual(renderer.render(doc), "42")

    def test_markdown_with_scheme_renderer(self):
        self.assertEqual(
            mistletoe.markdown("(define x (* 2 21))\nx", Scheme), "42"
        )

    def test_render_empty_document(self):
        with Scheme() as renderer:
            self.assertEqual(renderer.render(Document("")), "")

    def test_token_types_are_restored_after_render(self):
        with Scheme():
            pass
        # a plain markdown document still parses with the default tokens
        self.assertIn(
            "<p>hello</p>", mistletoe.markdown("hello")
        )
