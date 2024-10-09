from unittest import TestCase, mock
from mistletoe import span_token, Document, token
from mistletoe.span_token import tokenize_inner
from mistletoe.contrib.github_wiki import GithubWiki, GithubWikiRenderer


class TestGithubWiki(TestCase):
    def setUp(self):
        token._root_node = Document([])
        self.renderer = GithubWikiRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_parse(self):
        MockRawText = mock.Mock()
        RawText = span_token._token_types.pop()
        span_token._token_types.append(MockRawText)
        try:
            tokens = tokenize_inner('text with [[wiki | target]]')
            token = tokens[1]
            self.assertIsInstance(token, GithubWiki)
            self.assertEqual(token.target, 'target')
            MockRawText.assert_has_calls([mock.call('text with '), mock.call('wiki')])
        finally:
            span_token._token_types[-1] = RawText

    def test_render(self):
        token = next(iter(tokenize_inner('[[wiki|target]]')))
        output = '<a href="target">wiki</a>'
        self.assertEqual(self.renderer.render(token), output)
