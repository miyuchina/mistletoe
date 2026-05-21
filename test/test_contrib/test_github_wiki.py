import time
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

    def test_parse_variant_spacing_and_pipes(self):
        test_cases = [
            ('[[wiki | target]]', 'wiki', 'target'),
            ('[[ wiki | target ]]', 'wiki', 'target'),
            ('[[a | b | c]]', 'a', 'b | c'),
        ]
        for source, label, target in test_cases:
            with self.subTest(source=source):
                token = next(iter(tokenize_inner(source)))
                self.assertIsInstance(token, GithubWiki)
                self.assertEqual(token.target, target)
                self.assertEqual(self.renderer.render_inner(token), label)

    def test_malformed_input_is_rejected_quickly(self):
        malformed_inputs = [
            '[[' + ' ' * 10000 + '|' + ' ' * 10000 + ']',
            '[[' + ' ' * 10000 + ']]',
        ]
        for source in malformed_inputs:
            with self.subTest(length=len(source)):
                start = time.perf_counter()
                match = GithubWiki.pattern.match(source)
                elapsed = time.perf_counter() - start
                self.assertLess(elapsed, 1.0)
                self.assertIsNone(match)
