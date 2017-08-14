import unittest
import test.helpers as helpers
import mistletoe.span_token as span_token
from plugins.github_wiki import GithubWikiRenderer

class TestGithubWiki(unittest.TestCase):
    def test_context(self):
        with GithubWikiRenderer():
            self.assertTrue(hasattr(span_token, 'GithubWiki'))
        self.assertFalse(hasattr(span_token, 'GithubWiki'))

    def test_parse(self):
        with GithubWikiRenderer():
            t = span_token.Strong('text with [[wiki | target]].')
            c0 = span_token.RawText('text with ')
            c1 = span_token.GithubWiki('[[wiki|target]]')
            c2 = span_token.RawText('.')
            l = list(t.children)
            helpers.check_equal(self, l[0], c0)
            helpers.check_equal(self, l[1], c1)
            helpers.check_equal(self, l[2], c2)

    def test_render(self):
        with GithubWikiRenderer() as renderer:
            t = span_token.GithubWiki('[[wiki|target]]')
            target = '<a href="target">wiki</a>'
            self.assertEqual(renderer.render(t), target)
