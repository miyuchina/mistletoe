import unittest
import mistletoe
import test.helpers as helpers
from plugins.github_wiki import Context

class TestGithubWiki(unittest.TestCase):
    def test_context(self):
        with Context():
            self.assertTrue(hasattr(mistletoe.span_token, 'GitHubWiki'))
        self.assertFalse(hasattr(mistletoe.span_token, 'GitHubWiki'))

    def test_parse(self):
        with Context():
            t = mistletoe.span_token.Strong('text with [[wiki | target]].')
            c0 = mistletoe.span_token.RawText('text with ')
            c1 = mistletoe.span_token.GitHubWiki('[[wiki|target]]')
            c2 = mistletoe.span_token.RawText('.')
            l = list(t.children)
            helpers.check_equal(self, l[0], c0)
            helpers.check_equal(self, l[1], c1)
            helpers.check_equal(self, l[2], c2)

    def test_render(self):
        with Context() as c:
            t = mistletoe.span_token.GitHubWiki('[[wiki|target]]')
            self.assertEqual(c.render(t), '<a href="target">wiki</a>')
