from unittest import TestCase, mock
from mistletoe.span_token import tokenize_inner
from plugins.github_wiki import GithubWiki, GithubWikiRenderer


class TestGithubWiki(TestCase):
    def setUp(self):
        self.renderer = GithubWikiRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    @mock.patch('mistletoe.span_token.RawText')
    def test_parse(self, MockRawText):
        tokens = tokenize_inner('text with [[wiki | target]]')
        next(tokens)
        MockRawText.assert_called_with('text with ')
        token = next(tokens)
        self.assertIsInstance(token, GithubWiki)
        self.assertEqual(token.target, 'target')
        next(token.children)
        MockRawText.assert_called_with('wiki')

    def test_render(self):
        token = next(tokenize_inner('[[wiki|target]]'))
        output = '<a href="target">wiki</a>'
        self.assertEqual(self.renderer.render(token), output)
