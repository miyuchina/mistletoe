"""Deterministic regressions for overlapping parser and renderer contexts."""

import asyncio
import html
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from unittest import TestCase
from unittest.mock import patch

from mistletoe import Document, HtmlRenderer, block_token, core_tokens, markdown, span_token, token
from mistletoe.block_tokenizer import FileWrapper
from mistletoe.contrib.github_wiki import GithubWiki, GithubWikiRenderer
from mistletoe.latex_renderer import LaTeXRenderer
from mistletoe.markdown_renderer import MarkdownRenderer


TIMEOUT = 5


class TestRendererContexts(TestCase):
    def test_construction_has_no_side_effects(self):
        with HtmlRenderer(process_html_tokens=False) as renderer:
            MarkdownRenderer()
            GithubWikiRenderer()
            self.assertEqual(renderer.render(Document('a\n\nb')), '<p>a</p>\n<p>b</p>\n')
            self.assertEqual(renderer.render(Document('<em>x</em>')), '<p>&lt;em&gt;x&lt;/em&gt;</p>\n')

    def test_nested_context_restores_outer_configuration(self):
        source = 'a\n\nb\n\n[label]: /target\n\n[label]\n'
        for outer_cls in (HtmlRenderer, MarkdownRenderer):
            for inner_cls in (HtmlRenderer, MarkdownRenderer):
                with self.subTest(outer=outer_cls, inner=inner_cls):
                    with outer_cls() as outer:
                        before = outer.render(Document(source))
                        with inner_cls() as inner:
                            self.assertEqual(inner.render(Document(source)), inner.render(inner.parse(source)))
                        self.assertEqual(outer.render(Document(source)), before)

    def test_same_renderer_can_be_nested_and_reused(self):
        renderer = MarkdownRenderer()
        source = 'a\n\nb\n'
        for _ in range(2):
            with renderer:
                with renderer:
                    self.assertEqual(renderer.render(Document(source)), source)
                self.assertEqual(renderer.render(Document(source)), source)

    def test_exception_restores_outer_configuration(self):
        with MarkdownRenderer() as outer:
            with self.assertRaisesRegex(RuntimeError, 'failure'):
                with HtmlRenderer():
                    raise RuntimeError('failure')
            self.assertEqual(outer.render(Document('a\n\nb')), 'a\n\nb\n')

    def test_explicit_parse_uses_own_configuration(self):
        html_renderer = HtmlRenderer(process_html_tokens=False)
        markdown_renderer = MarkdownRenderer()
        source = '<em>x</em>\n\na\n'
        expected = '<p>&lt;em&gt;x&lt;/em&gt;</p>\n<p>a</p>\n'
        self.assertEqual(html_renderer.render(html_renderer.parse(source)), expected)
        with markdown_renderer:
            self.assertEqual(html_renderer.render(html_renderer.parse(source)), expected)
            self.assertEqual(markdown_renderer.render(Document(source)), source)

    def test_markdown_ast_can_be_rendered_by_other_renderers(self):
        source = 'a\n\nb\n\n[label]: /target\n\n[label]\n'
        for renderer_cls in (HtmlRenderer, LaTeXRenderer):
            with self.subTest(renderer=renderer_cls):
                with renderer_cls() as renderer:
                    expected = renderer.render(Document(source))
                    with MarkdownRenderer():
                        self.assertEqual(renderer.render(Document(source)), expected)

    def test_ambient_and_active_registrations_are_scoped(self):
        previous = span_token._token_types.get()
        self.addCleanup(span_token._token_types.set, previous)
        span_token.add_token(GithubWiki)
        renderer = HtmlRenderer()
        with renderer:
            span_token.remove_token(GithubWiki)
            outer = span_token._token_types.get()
            with HtmlRenderer():
                self.assertIn(GithubWiki, span_token._token_types.get())
                span_token.reset_tokens()
                self.assertNotIn(GithubWiki, span_token._token_types.get())
            self.assertEqual(span_token._token_types.get(), outer)
            self.assertNotIsInstance(renderer.parse('[[wiki|target]]').children[0].children[0], GithubWiki)
        self.assertIn(GithubWiki, span_token._token_types.get())

    def test_explicit_parse_honors_active_token_changes(self):
        with HtmlRenderer() as renderer:
            span_token.remove_token(span_token.Strikethrough)
            self.assertEqual(renderer.render(renderer.parse('~~text~~')), '<p>~~text~~</p>\n')

    def test_high_level_conversion_restores_enclosing_renderer(self):
        with MarkdownRenderer() as renderer:
            self.assertEqual(markdown('a\n\nb'), '<p>a</p>\n<p>b</p>\n')
            self.assertEqual(renderer.render(Document('a\n\nb')), 'a\n\nb\n')


class TestParseState(TestCase):
    def test_nested_documents_restore_root(self):
        original_tokenize = block_token.tokenize
        roots = []

        def tokenize(lines):
            if lines[0] == '[outer]: /outer\n':
                root = token._root_node.get()
                nested = Document('[inner]: /inner\n\n[inner]')
                roots.append((root, token._root_node.get(), nested))
            return original_tokenize(lines)

        previous_root = token._root_node.get()
        with patch.object(block_token, 'tokenize', side_effect=tokenize):
            outer = Document('[outer]: /outer\n\n[outer]')
        self.assertIs(roots[0][0], outer)
        self.assertIs(roots[0][1], outer)
        self.assertEqual(outer.children[0].children[0].target, '/outer')
        self.assertEqual(roots[0][2].children[0].children[0].target, '/inner')
        self.assertIs(token._root_node.get(), previous_root)

    def test_failed_parse_restores_root_and_configuration(self):
        previous_root = token._root_node.get()
        with MarkdownRenderer() as outer:
            with patch.object(block_token, 'tokenize', side_effect=RuntimeError('failure')):
                with self.assertRaisesRegex(RuntimeError, 'failure'):
                    HtmlRenderer().parse('text')
            self.assertIs(token._root_node.get(), previous_root)
            self.assertEqual(outer.render(Document('a\n\nb')), 'a\n\nb\n')

    def test_nested_inline_parse_restores_code_matches(self):
        class Nested(span_token.SpanToken):
            @classmethod
            def find(cls, source):
                if source == '`outer`':
                    nested = span_token.tokenize_inner('`nested`')
                    self.assertEqual(nested[0].children[0].content, 'nested')
                return ()

        previous = span_token._token_types.get()
        self.addCleanup(span_token._token_types.set, previous)
        # Run after CoreTokens has found code matches, before InlineCode uses them.
        span_token.add_token(Nested, position=4)
        parsed = span_token.tokenize_inner('`outer`')
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].children[0].content, 'outer')

    def test_nested_document_inside_quote_has_own_setext_state(self):
        original = block_token.tokenizer.tokenize_block
        nested = []

        def tokenize_block(lines, *args, **kwargs):
            if kwargs.get('depth') == 1:
                nested.append(Document('heading\n===\n'))
            return original(lines, *args, **kwargs)

        with patch.object(block_token.tokenizer, 'tokenize_block', side_effect=tokenize_block):
            Document('> quote\n')
        self.assertIsInstance(nested[0].children[0], block_token.SetextHeading)

    def test_failed_inline_parse_restores_state(self):
        previous = core_tokens._code_matches.get()
        with patch.object(span_token.InlineCode, 'find', side_effect=RuntimeError('failure')):
            with self.assertRaisesRegex(RuntimeError, 'failure'):
                span_token.tokenize_inner('`broken`')
        self.assertIs(core_tokens._code_matches.get(), previous)
        self.assertEqual(span_token.tokenize_inner('`next`')[0].children[0].content, 'next')

    def test_interleaved_block_start_and_read(self):
        cases = (
            (block_token.Heading, '# first\n', '### second\n'),
            (block_token.CodeFence, '```first\none\n```\n', '~~~second\ntwo\n~~~\n'),
            (block_token.HtmlBlock, '<!--\none\n-->\n', '<script>\ntwo\n</script>\n'),
        )
        for token_cls, first, second in cases:
            with self.subTest(token=token_cls):
                sources = (first, second)
                expected = [token_cls.read(FileWrapper(source.splitlines(keepends=True))) for source in sources]
                barrier = Barrier(2, timeout=TIMEOUT)

                def worker(source):
                    lines = source.splitlines(keepends=True)
                    self.assertTrue(token_cls.start(lines[0]))
                    barrier.wait()
                    return token_cls.read(iter(lines))

                with ThreadPoolExecutor(max_workers=2) as pool:
                    self.assertEqual(list(pool.map(worker, sources)), expected)

    def test_interleaved_inline_matches(self):
        barrier = Barrier(2, timeout=TIMEOUT)

        def worker(source):
            span_token.CoreTokens.find(source)
            barrier.wait()
            return [match.group(2) for match in span_token.InlineCode.find(source)]

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(list(pool.map(worker, ('`first`', '`second`'))), [['first'], ['second']])

    def test_quote_does_not_change_setext_parsing_in_another_thread(self):
        entered = Event()
        release = Event()
        original = block_token.tokenizer.tokenize_block

        def tokenize_block(lines, *args, **kwargs):
            if kwargs.get('depth') == 1:
                entered.set()
                if not release.wait(TIMEOUT):
                    raise TimeoutError('quote parser was not released')
            return original(lines, *args, **kwargs)

        with patch.object(block_token.tokenizer, 'tokenize_block', side_effect=tokenize_block):
            with ThreadPoolExecutor(max_workers=1) as pool:
                quote = pool.submit(Document, '> quote\n')
                try:
                    self.assertTrue(entered.wait(TIMEOUT))
                    heading = Document('heading\n===\n').children[0]
                    self.assertIsInstance(heading, block_token.SetextHeading)
                finally:
                    release.set()
                quote.result(timeout=TIMEOUT)


class TestConcurrentRenderers(TestCase):
    def test_custom_renderer_extras_are_isolated(self):
        barrier = Barrier(2, timeout=TIMEOUT)

        def worker(renderer_cls):
            renderer = renderer_cls()
            barrier.wait()
            with renderer:
                barrier.wait()
                output = renderer.render(Document('[[wiki|target]]'))
                barrier.wait()
                return output

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(list(pool.map(worker, (GithubWikiRenderer, HtmlRenderer))),
                             ['<p><a href="target">wiki</a></p>\n', '<p>[[wiki|target]]</p>\n'])

    def test_threads_keep_renderer_configurations_and_references_separate(self):
        barrier = Barrier(4, timeout=TIMEOUT)

        class Gate(block_token.BlockToken):
            def __init__(self, result):
                self.children = []

            @staticmethod
            def start(line):
                return line == '!gate\n'

            @staticmethod
            def read(lines):
                next(lines)
                barrier.wait()
                return ()

        class Wait(span_token.SpanToken):
            @classmethod
            def find(cls, source):
                barrier.wait()
                return ()

        def worker(index):
            renderer_cls = (HtmlRenderer, MarkdownRenderer, LaTeXRenderer, GithubWikiRenderer)[index]

            def render_gate(token, **kwargs):
                return [] if renderer_cls is MarkdownRenderer else ''

            source = '!gate\n\n[label]: /target{}\n\n[label] `code{}`\n'.format(index, index)
            with renderer_cls() as renderer:
                block_token.add_token(Gate)
                span_token.add_token(Wait)
                renderer.render_map['Gate'] = render_gate
                document = Document(source)
                self.assertEqual(document.footnotes['label'][0], '/target{}'.format(index))
                self.assertEqual(document.children[-1].children[-1].children[0].content, 'code{}'.format(index))
                output = renderer.render(document)
                barrier.wait()
                return output

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(worker, range(4)))
        for index, output in enumerate(results):
            self.assertIn('/target{}'.format(index), output)
            self.assertIn('code{}'.format(index), output)

    def test_html_options_are_independent_between_threads(self):
        barrier = Barrier(2, timeout=TIMEOUT)

        def worker(process_html):
            with HtmlRenderer(process_html_tokens=process_html) as renderer:
                barrier.wait()
                output = renderer.render(Document('<em>x</em>'))
                barrier.wait()
                return output

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(list(pool.map(worker, (True, False))),
                             ['<p><em>x</em></p>\n', '<p>&lt;em&gt;x&lt;/em&gt;</p>\n'])

    def test_parsing_does_not_modify_stdlib_entity_decoding(self):
        entered = Event()
        release = Event()
        original_pattern = html._charref

        class Wait(span_token.SpanToken):
            @classmethod
            def find(cls, source):
                entered.set()
                if not release.wait(TIMEOUT):
                    raise TimeoutError('inline parser was not released')
                return ()

        class Renderer(HtmlRenderer):
            def render_wait(self, token):
                return ''

        def worker():
            with Renderer(Wait) as renderer:
                return renderer.render(Document('&amp; &amp'))

        with ThreadPoolExecutor(max_workers=1) as pool:
            result = pool.submit(worker)
            try:
                self.assertTrue(entered.wait(TIMEOUT))
                self.assertIs(html._charref, original_pattern)
                self.assertEqual(html.unescape('&#65 &amp'), 'A &')
            finally:
                release.set()
            self.assertEqual(result.result(timeout=TIMEOUT), '<p>&amp; &amp;amp</p>\n')

    def test_async_tasks_isolate_inherited_token_registrations(self):
        class Extra(span_token.SpanToken):
            pattern = re.compile(r'(@extra)')

        async def scenario():
            modified = asyncio.Event()
            checked = asyncio.Event()

            async def modifying_task():
                span_token.add_token(Extra)
                span_token.remove_token(span_token.Strikethrough)
                modified.set()
                await asyncio.wait_for(checked.wait(), TIMEOUT)
                self.assertIn(Extra, span_token._token_types.get())
                self.assertNotIn(span_token.Strikethrough, span_token._token_types.get())

            async def observing_task():
                await asyncio.wait_for(modified.wait(), TIMEOUT)
                try:
                    self.assertNotIn(Extra, span_token._token_types.get())
                    self.assertIn(span_token.Strikethrough, span_token._token_types.get())
                    with HtmlRenderer() as renderer:
                        await asyncio.sleep(0)
                        self.assertEqual(renderer.render(Document('a\n\nb')), '<p>a</p>\n<p>b</p>\n')
                finally:
                    checked.set()

            for active in (False, True):
                modified.clear()
                checked.clear()
                if active:
                    with MarkdownRenderer() as renderer:
                        await asyncio.gather(modifying_task(), observing_task())
                        self.assertEqual(renderer.render(Document('a\n\nb')), 'a\n\nb\n')
                else:
                    await asyncio.gather(modifying_task(), observing_task())

        asyncio.run(scenario())
