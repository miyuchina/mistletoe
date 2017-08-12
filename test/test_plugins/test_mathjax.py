import unittest
from mistletoe import Document
from plugins.mathjax import MathJaxRenderer

class TestMathJaxRenderer(unittest.TestCase):
    mathjax_src = '<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-MML-AM_CHTML"></script>\n'

    def test_render_html(self):
        with MathJaxRenderer() as renderer:
            token = Document(['# heading 1\n', 'paragraph\n'])
            output = renderer.render(token)
            target = '<h1>heading 1</h1>\n<p>paragraph</p>\n'
            target += self.mathjax_src
            self.assertEqual(output, target)

    def test_render_math(self):
        with MathJaxRenderer() as renderer:
            raw = ['# heading 1\n', '$$paragraph$$\n', 'with $ math $\n']
            token = Document(raw)
            output = renderer.render(token)
            target = '<h1>heading 1</h1>\n<p>$$paragraph$$ with $$ math $$</p>\n'
            target += self.mathjax_src
            self.assertEqual(output, target)
