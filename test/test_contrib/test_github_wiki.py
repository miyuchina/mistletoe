from unittest import TestCase, mock
from mistletoe.span_token import tokenize_inner, _token_types
from contrib.github_wiki import GithubWiki, GithubWikiRenderer


class TestGithubWiki(TestCase):
    def setUp(self):
        self.renderer = GithubWikiRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_parse(self):
        MockRawText = mock.Mock(autospec='mistletoe.span_token.RawText')
        RawText = _token_types.pop()
        _token_types.append(MockRawText)
        try:
            tokens = tokenize_inner('text with [[wiki | target]]')
            next(tokens)
            MockRawText.assert_called_with('text with ')
            token = next(tokens)
            self.assertIsInstance(token, GithubWiki)
            self.assertEqual(token.target, 'target')
            next(iter(token.children))
            MockRawText.assert_called_with('wiki')
        finally:
            _token_types[-1] = RawText

    def test_render(self):
        token = next(tokenize_inner('[[wiki|target]]'))
        output = '<a href="target">wiki</a>'
        self.assertEqual(self.renderer.render(token), output)

