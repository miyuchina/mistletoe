from unittest import TestCase

from mistletoe.base_renderer import BaseRenderer
from mistletoe.span_token import RawText


class TestBaseRenderer(TestCase):
    def test_render_inner_handles_tokens_without_children(self):
        renderer = BaseRenderer()
        for children in (None, []):
            with self.subTest(children=children):
                token = RawText('leaf')
                if children is not None:
                    token.children = children
                self.assertEqual(renderer.render_inner(token), '')
