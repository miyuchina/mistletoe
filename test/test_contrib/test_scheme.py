from unittest import TestCase

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
