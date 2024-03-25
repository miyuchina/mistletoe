from unittest import TestCase, mock
from unittest import TestCase
from mistletoe.html_renderer import HTMLRenderer


class TestHTMLAttributes(TestCase):
    def setUp(self):
        self.renderer = HTMLRenderer()
        self.renderer.render_inner = mock.Mock(return_value='inner')
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def _test_token(self, token_name, output, children=True,
                    without_attrs=None, **kwargs):
        render_func = self.renderer.render_map[token_name]
        children = mock.MagicMock(spec=list) if children else None
        mock_token = mock.Mock(children=children, **kwargs)
        without_attrs = without_attrs or []
        for attr in without_attrs:
            delattr(mock_token, attr)
        self.assertEqual(render_func(mock_token), output)

    def test_inline_code(self):
        from mistletoe.span_token import tokenize_inner
        rendered = self.renderer.render(tokenize_inner('`foo`')[0])
        self.assertEqual(rendered, '<code>foo</code>')
        rendered = self.renderer.render(tokenize_inner('`` \\[\\` ``')[0])
        self.assertEqual(rendered, '<code>\\[\\`</code>')

    def test_image(self):
        output = '<img src="src" alt="" title="title" />'
        self._test_token('Image', output, src='src', title='title')

    def test_link(self):
        output = '<a href="target" title="title">inner</a>'
        self._test_token('Link', output, target='target', title='title')

    def test_autolink(self):
        output = '<a href="link">inner</a>'
        self._test_token('AutoLink', output, target='link', mailto=False)

    def test_heading(self):
        output = '<h3>inner</h3>'
        self._test_token('Heading', output, level=3)

    def test_quote(self):
        output = '<blockquote>\n</blockquote>'
        self._test_token('Quote', output)

    def test_paragraph(self):
        self._test_token('Paragraph', '<p>inner</p>')

    def test_block_code(self):
        from mistletoe.block_token import tokenize
        rendered = self.renderer.render(tokenize(['```sh\n', 'foo\n', '```\n'])[0])
        output = '<pre><code class="language-sh">foo\n</code></pre>'
        self.assertEqual(rendered, output)

    def test_block_code_no_language(self):
        from mistletoe.block_token import tokenize
        rendered = self.renderer.render(tokenize(['```\n', 'foo\n', '```\n'])[0])
        output = '<pre><code>foo\n</code></pre>'
        self.assertEqual(rendered, output)

    def test_list(self):
        output = '<ul>\n\n</ul>'
        self._test_token('List', output, start=None)

    def test_list_item(self):
        output = '<li></li>'
        self._test_token('ListItem', output)

    def test_table_with_header(self):
        func_path = 'mistletoe.html_renderer.HTMLRenderer.render_table_row'
        with mock.patch(func_path, autospec=True) as mock_func:
            mock_func.return_value = 'row'
            output = ('<table>\n'
                        '<thead>\nrow</thead>\n'
                        '<tbody>\ninner</tbody>\n'
                      '</table>')
            self._test_token('Table', output)

    def test_table_without_header(self):
        func_path = 'mistletoe.html_renderer.HTMLRenderer.render_table_row'
        with mock.patch(func_path, autospec=True) as mock_func:
            mock_func.return_value = 'row'
            output = '<table>\n<tbody>\ninner</tbody>\n</table>'
            self._test_token('Table', output, without_attrs=['header',])

    def test_table_row(self):
        self._test_token('TableRow', '<tr>\n</tr>\n')

    def test_table_cell(self):
        output = '<td align="left">inner</td>\n'
        self._test_token('TableCell', output, align=None)
        
    def test_table_cell0(self):
        output = '<td align="center">inner</td>\n'
        self._test_token('TableCell', output, align=0)
        
    def test_table_cell1(self):
        output = '<td align="right">inner</td>\n'
        self._test_token('TableCell', output, align=1)

    def test_thematic_break(self):
        self._test_token('ThematicBreak', '<hr />', children=False)

    def test_html_block(self):
        content = output = '<h1>hello</h1>\n<p>this is\na paragraph</p>\n'
        self._test_token('HTMLBlock', output,
                         children=False, content=content)

    def test_line_break(self):
        self._test_token('LineBreak', '<br />\n', children=False, soft=False)

    def test_document(self):
        self._test_token('Document', '', footnotes={})

    def test_document(self):
        from mistletoe import markdown, block_token
        from mistletoe.html_attributes_renderer import HTMLAttributesRenderer
        mdFull = """\
            ## Blockquotes

            ${class:foobar}
            > Blockquotes can also be nested...
            ${class:foobar-two}
            >> ...by using additional greater-than signs right next to each other...
            ${class:foobar-three}
            > > > ...or with spaces between arrows.


            # Unordered

            ${class:foobar}
            + Create a list by starting a line with `+`, `-`, or `*`
            + item twos


            # Ordered

            ${class:foobar}
            1. Lorem ipsum dolor sit amet
            2. another thing


            ## Tables
            ${class:foobar > class:barbar}
            | Option | Description |
            | ------ | ----------- |
            | data   | path to data files to supply the data that will be passed into templates. |
            | engine | engine to be used for processing templates. Handlebars is the default. |
            | ext    | extension to be used for dest files. |
            """

        mdInput = """\
${class:foobar}
# Mistletoe is Awesome

${id:todos, tabindex:100 > class:list-item}
- Push Code
- Get Groceries
    - Veggies
    - Fruits
        - apples
        - oranges
- Hang up the mistletoe

${class:img-sm}
![foo](https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg "toof")

${ > class:btn-link, aria-label:Kiss Me under the mistle toe}
[some link](https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg "toof")\
            """
        
        mdOutput = """\
            <h1 class="foobar" id="mistletoe-is-awesome" tabindex="1">Mistletoe is Awesome</h1>
            <ul id="todos" tabindex="100">
                <li class="list-item" tabindex="1">Push Code</li>
                <li class="list-item" tabindex="1">Get Groceries
                    <ul id="todos-0" tabindex="1">
                        <li class="list-item" tabindex="1">Veggies</li>
                        <li class="list-item" tabindex="1">Fruits
                            <ul id="todos-0-1" tabindex="1">
                                <li class="list-item" tabindex="1">apples</li>
                                <li class="list-item" tabindex="1">oranges</li>
                            </ul>
                        </li>
                    </ul>
                </li>
                <li class="list-item" tabindex="1">Hang up the mistletoe</li>
            </ul>
            <p class="img-sm" tabindex="1"><img src="https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg" alt="foo" title="toof" tabindex="1" /></p>
            <p tabindex="1"><a href="https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg" title="toof" class="btn-link" aria-label="Kiss Me under the mistle toe" tabindex="1">some link</a></p>
            """
        
        block_token.HTMLAttributes.configure({"enable_auto_ids": True})
        # ohtml = markdown(full, HTMLAttributesRenderer)
        html = markdown(mdInput, HTMLAttributesRenderer)
        # isequal = html.strip().replace('\n',' ') == ' '.join(mdOutput.split())
        self.assertEqual(html.strip().replace('\n',' '), ' '.join(mdOutput.split()))
