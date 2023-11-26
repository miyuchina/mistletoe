<h1>Developer's Guide<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right' width='128' height='128'></h1>

This document describes usage of mistletoe and its API
from the developer's point of view.

Understanding the AST and the tokens
------------------------------------

When a markdown document gets parsed by mistletoe, the result is represented
as an _abstract syntax tree (AST)_, stored in an instance of `Document`.
This object contains a hierarchy of all the various _tokens_ which were recognized
during the parsing process, for example, `Paragraph`, `Heading`, and `RawText`.

The tokens which represent a line or a block of lines in the input markdown
are called _block tokens_. Examples include `List`, `Paragraph`, `ThematicBreak`,
and also the `Document` itself.

The tokens which represent the actual content within a block are called _span tokens_,
or, with CommonMark terminology, _inline tokens_.
In this category you will find tokens like `RawText`, `Link`, and `Emphasis`.

Block tokens may have block tokens, span tokens, or no tokens at all as children
in the AST; this depends on the type of token. Span tokens may *only* have span
tokens as children.

In order to see what exactly gets parsed, one can simply use the `AstRenderer`
on a given markdown input, for example:

```sh
mistletoe text.md --renderer mistletoe.ast_renderer.AstRenderer
```

Say that the input file contains for example:

```markdown
# Heading 1

text

# Heading 2

[link](https://www.example.com)
```

Then we will get this JSON output from the AST renderer:

```json
{
  "type": "Document",
  "footnotes": {},
  "line_number": 1,
  "children": [
    {
      "type": "Heading",
      "line_number": 1,
      "level": 1,
      "children": [
        {
          "type": "RawText",
          "content": "Heading 1"
        }
      ]
    },
    {
      "type": "Paragraph",
      "line_number": 3,
      "children": [
        {
          "type": "RawText",
          "content": "text"
        }
      ]
    },
    {
      "type": "Heading",
      "line_number": 5,
      "level": 1,
      "children": [
        {
          "type": "RawText",
          "content": "Heading 2"
        }
      ]
    },
    {
      "type": "Paragraph",
      "line_number": 7,
      "children": [
        {
          "type": "Link",
          "target": "https://www.example.com",
          "title": "",
          "children": [
            {
              "type": "RawText",
              "content": "link"
            }
          ]
        }
      ]
    }
  ]
}
```

### Line numbers

mistletoe records the starting line of all block tokens that it encounters during
parsing and stores it as the `line_number` attribute of each token.
(This feature is not available for span tokens yet.)

Rendering
---------
Sometimes all you need is the information from the AST. But more often, you'll
want to take that information and turn it into some other format like HTML.
This is called _rendering_. mistletoe provides a set of built-in renderers for
different formats, and it's also possible to define your own renderer.

When passing an AST to a renderer, the tree is recursively traversed
and methods corresponding to individual token types get called on the renderer
in order to create the output in the desired format.

Creating a custom token and renderer
------------------------------------

Here's an example of how to add GitHub-style wiki links to the parsing process,
and provide a renderer for this new token.

### A new token

GitHub wiki links are span-level tokens, meaning that they reside inline,
and don't really look like chunky paragraphs. To write a new span-level
token, all we need to do is make a subclass of `SpanToken`:

```python
from mistletoe.span_token import SpanToken

class GithubWiki(SpanToken):
    pass
```

mistletoe uses regular expressions to search for span-level tokens in the
parsing process. As a refresher, GitHub wiki looks something like this:
`[[alternative text | target]]`. We define a class variable, `pattern`,
that stores the compiled regex:

```python
class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")
    def __init__(self, match):
        pass
```

The regex will be picked up by `SpanToken.find`, which is used by the
tokenizer to find all tokens of its kind in the document.
If regexes are too limited for your use case, consider overriding
the `find` method; it should return a list of all token occurrences.

Three other class variables are available for our custom token class,
and their default values are shown below:

```python
class SpanToken:
    parse_group = 1
    parse_inner = True
    precedence = 5
```

Note that alternative text can also contain other span-level tokens. For
example, `[[*alt*|link]]` is a GitHub link with an `Emphasis` token as its
child. To parse child tokens, `parse_inner` should be set to `True`
(the default value in this case), and `parse_group` should correspond
to the match group in which child tokens might occur
(also the default value, 1, in this case).

Once these two class variables are set correctly,
`GithubWiki.children` attribute will automatically be set to
the list of child tokens.
Note that there is no need to manually set this attribute,
unlike previous versions of mistletoe.

Lastly, the `SpanToken` constructors take a regex match object as its argument.
We can simply store off the `target` attribute from `match_obj.group(2)`.

```python
from mistletoe.span_token import SpanToken

class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")
    def __init__(self, match_obj):
        self.target = match_obj.group(2)
```

There you go: a new token in 5 lines of code.

### Side note about precedence

Normally there is no need to override the `precedence` value of a custom token.
The default value is the same as `InlineCode`, `AutoLink` and `HtmlSpan`,
which means that whichever token comes first will be parsed. In our case:

```markdown
`code with [[ text` | link ]]
```

... will be parsed as:

```html
<code>code with [[ text</code> | link ]]
```

If we set `GithubWiki.precedence = 6`, we have:

```html
`code with <a href="link">text`</a>
```

### A new renderer

Adding a custom token to the parsing process usually involves a lot
of nasty implementation details. Fortunately, mistletoe takes care
of most of them for you. Simply passing your custom token class to 
`super().__init__()` does the trick:

```python
from mistletoe.html_renderer import HtmlRenderer

class GithubWikiRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(GithubWiki)
```

We then only need to tell mistletoe how to render our new token:

```python
def render_github_wiki(self, token):
    template = '<a href="{target}">{inner}</a>'
    target = token.target
    inner = self.render_inner(token)
    return template.format(target=target, inner=inner)
```
Cleaning up, we have our new renderer class:

```python
from mistletoe.html_renderer import HtmlRenderer, escape_url

class GithubWikiRenderer(HtmlRenderer):
    def __init__(self):
        super().__init__(GithubWiki)

    def render_github_wiki(self, token):
        template = '<a href="{target}">{inner}</a>'
        target = escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)
```

### Take it for a spin?

It is preferred that all mistletoe's renderers be used as context managers.
This is to ensure that your custom tokens are cleaned up properly, so that
you can parse other Markdown documents with different token types in the
same program.

```python
from mistletoe import Document
from contrib.github_wiki import GithubWikiRenderer

with open('foo.md', 'r') as fin:
    with GithubWikiRenderer() as renderer:
        rendered = renderer.render(Document(fin))
```

For more info, take a look at the `base_renderer` module in mistletoe.
The docstrings might give you a more granular idea of customizing mistletoe
to your needs.

Markdown to Markdown parsing-and-rendering
------------------------------------------

Suppose you have some Markdown that you want to process and then output
as Markdown again. Thanks to the text-like nature of Markdown, it is often
possible to do this with text search-and-replace tools... but not always. For
example, if you want to replace a text fragment in the plain text, but not
in the embedded code samples, then the search-and-replace approach won't work.

In this case you can use mistletoe's `MarkdownRenderer`:
1. Parse Markdown to an AST (usually held in a `Document` token).
2. Make modifications to the AST.
3. Render back to Markdown using `MarkdownRenderer.render()`.

Here is an example of how you can replace text in selected parts of the AST:

```python
import mistletoe
from mistletoe.block_token import BlockToken, Heading, Paragraph, SetextHeading
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.span_token import InlineCode, RawText, SpanToken

def update_text(token: SpanToken):
    """Update the text contents of a span token and its children.
    `InlineCode` tokens are left unchanged."""
    if isinstance(token, RawText):
        token.content = token.content.replace("mistletoe", "The Amazing mistletoe")

    if not isinstance(token, InlineCode) and hasattr(token, "children"):
        for child in token.children:
            update_text(child)

def update_block(token: BlockToken):
    """Update the text contents of paragraphs and headings within this block,
    and recursively within its children."""
    if isinstance(token, (Paragraph, SetextHeading, Heading)):
        for child in token.children:
            update_text(child)

    for child in token.children:
        if isinstance(child, BlockToken):
            update_block(child)

with open("README.md", "r") as fin:
    with MarkdownRenderer() as renderer:
        document = mistletoe.Document(fin)
        update_block(document)
        md = renderer.render(document)
        print(md)
```

The `MarkdownRenderer` can also reflow the text in the document to a given
maximum line length. And it can do so while preserving the formatting of code
blocks and other tokens where line breaks matter. To use this feature,
specify a `max_line_length` parameter in the call to the `MarkdownRenderer`
constructor.
