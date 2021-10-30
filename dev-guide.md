<h1>Developer's Guide<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right' width='128' height='128'></h1>

This document describes usage of mistletoe and its API
from the developer's point of view.

Understanding the AST
---------------------

When a markdown document gets parsed by mistletoe, the result is represented
as an "abstract syntax tree" (AST), stored in an instance of `Document`.
This object contains a hierarchy of
all the various tokens which were recognized during the parsing process.

In order to see what exactly gets parsed, one can simply use the `ASTRenderer`
on a given markdown input, for example:

```sh
mistletoe text.md --renderer mistletoe.ast_renderer.ASTRenderer
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
  "children": [
    {
      "type": "Heading",
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
      "children": [
        {
          "type": "RawText",
          "content": "text"
        }
      ]
    },
    {
      "type": "Heading",
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

When passing this tree to a renderer, it is recursively traversed
and methods corresponding to individual token types get called on the renderer
in order to create the output in the desired format.

Creating a custom renderer
--------------------------

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
The default value is the same as `InlineCode`, `AutoLink` and `HTMLSpan`,
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
from mistletoe.html_renderer import HTMLRenderer

class GithubWikiRenderer(HTMLRenderer):
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
from mistletoe.html_renderer import HTMLRenderer, escape_url

class GithubWikiRenderer(HTMLRenderer):
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
