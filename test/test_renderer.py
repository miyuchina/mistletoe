import unittest
import renderer

# TODO: refactor integration test

class TestRenderer(unittest.TestCase):
    def test_render_file(self):
        test_file = 'test/examples/basic_test.md'
        with open('test/examples/basic_out.html', 'r') as fin:
            output = ''.join(fin.readlines())
        self.assertEqual(renderer.render_file(test_file), output)

