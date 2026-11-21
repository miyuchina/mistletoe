import time
from unittest import mock

import pytest

from mistletoe import span_token, Document, token
from mistletoe.span_token import tokenize_inner
from mistletoe.contrib.github_wiki import GithubWiki, GithubWikiRenderer


class TestGithubWiki:
    @pytest.fixture(autouse=True)
    def setup_renderer(self):
        token._root_node = Document([])
        with GithubWikiRenderer() as renderer:
            self.renderer = renderer
            yield

    def test_parse(self):
        MockRawText = mock.Mock()
        RawText = span_token._token_types.pop()
        span_token._token_types.append(MockRawText)
        try:
            tokens = tokenize_inner('text with [[wiki | target]]')
            token = tokens[1]
            assert isinstance(token, GithubWiki)
            assert token.target == 'target'
            MockRawText.assert_has_calls([mock.call('text with '), mock.call('wiki')])
        finally:
            span_token._token_types[-1] = RawText

    def test_render(self):
        token = next(iter(tokenize_inner('[[wiki|target]]')))
        output = '<a href="target">wiki</a>'
        assert self.renderer.render(token) == output

    @pytest.mark.parametrize('source, label, target', [
        ('[[wiki | target]]', 'wiki', 'target'),
        ('[[ wiki | target ]]', 'wiki', 'target'),
        ('[[a | b | c]]', 'a', 'b | c'),
    ], ids=['standard', 'padded', 'extra-pipe'])
    def test_parse_variant_spacing_and_pipes(self, source, label, target):
        token = next(iter(tokenize_inner(source)))
        assert isinstance(token, GithubWiki)
        assert token.target == target
        assert self.renderer.render_inner(token) == label

    @pytest.mark.parametrize('source', [
        '[[' + ' ' * 200 + '|' + ' ' * 200 + ']',
        '[[' + ' ' * 6000 + ']]',
    ], ids=['missing_closing_marker', 'missing_pipe'])
    def test_malformed_input_is_rejected_quickly(self, source):
        start = time.perf_counter()
        match = GithubWiki.pattern.match(source)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0
        assert match is None
