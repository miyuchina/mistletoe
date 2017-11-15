<h1>mistletoe<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right'></h1>

[![Build Status][build-badge]][travis]
[![Coverage Status][cover-badge]][coveralls]
[![PyPI][pypi-badge]][pypi]
[![is wheel][wheel-badge]][pypi]

mistletoe is a Markdown parser in pure Python, designed to be fast, modular
and fully customizable.

mistletoe is not simply a Markdown-to-HTML transpiler. It is designed, from
the start, to parse Markdown into an abstract syntax tree. You can swap out
renderers for different output formats, without touching any of the core
components.

Remember to spell mistletoe in lowercase!

Features
--------
* **Fast**: mistletoe is as fast as the [fastest implementation][mistune]
  currently available: that is, over 4 times faster than
  [Python-Markdown][python-markdown], and much faster than
  [Python-Markdown2][python-markdown2].
  
  See the [performance](#performance) section for details.

* **Modular**: mistletoe is designed with modularity in mind. Its initial
  goal is to provide a clear and easy API to extend upon.

* **Customizable**: as of now, mistletoe can render Markdown documents to
  LaTeX, HTML and an abstract syntax tree out of the box. Writing a new
  renderer for mistletoe is a relatively trivial task.

Installation
------------
mistletoe requires Python 3.3 and above, including Python 3.7, the current
development branch. It is also tested on PyPy 5.8.0. Install mistletoe with
pip:

```sh
pip3 install mistletoe
```

Alternatively, clone the repo:

```sh
git clone https://github.com/miyuchina/mistletoe.git
cd mistletoe
pip3 install -e .
```

See the [contributing][contributing] doc for how to contribute to mistletoe.

Usage
-----

### Basic usage

Here's how you can use mistletoe in a Python script:

```python
import mistletoe

with open('foo.md', 'r') as fin:
    rendered = mistletoe.markdown(fin)
```

`mistletoe.markdown()` uses mistletoe's default settings: allowing HTML mixins
and rendering to HTML. The function also accepts an additional argument
`renderer`. To produce LaTeX output:

```python
import mistletoe
from mistletoe.latex_renderer import LaTeXRenderer

with open('foo.md', 'r') as fin:
    rendered = mistletoe.markdown(fin, LaTeXRenderer)
```

Finally, here's how you would manually specify extra tokens and a renderer
for mistletoe. In the following example, we use `HTMLRenderer` to render
the AST, which adds `HTMLBlock` and `HTMLSpan` to the normal parsing
process.

```python
from mistletoe import Document, HTMLRenderer

with open('foo.md', 'r') as fin:
    with HTMLRenderer() as renderer:
        rendered = renderer.render(Document(fin))
```

### From the command-line

pip installation enables mistletoe's commandline utility. Type the following
directly into your shell:

```sh
mistletoe foo.md
```

This will transpile `foo.md` into HTML, and dump the output to stdout. To save
the HTML, direct the output into a file:

```sh
mistletoe foo.md > out.html
```

Running `mistletoe` without specifying a file will land you in interactive
mode.  Like Python's REPL, interactive mode allows you to test how your
Markdown will be interpreted by mistletoe:

```
mistletoe [version 0.4] (interactive)
Type Ctrl-D to complete input, or Ctrl-C to exit.
>>> some **bold text**
... and some *italics*
... ^D
<html>
<body>
<p>some <strong>bold text</strong> and some <em>italics</em></p>
</body>
</html>
>>>
```

**New in version 0.3.1**: Emacs-style controls are now available.

Typing `Ctrl-D` tells mistletoe to interpret your input. `Ctrl-C` exits the
program.

Performance
-----------

mistletoe is the fastest Markdown parser implementation available in pure
Python; that is, on par with [mistune][mistune]. Try the benchmarks yourself by
running:

```sh
python3 test/benchmark.py
```

One of the significant bottlenecks of mistletoe compared to mistune, however,
is the function overhead. Because, unlike mistune, mistletoe chooses to split
functionality into modules, function lookups can take significantly longer than
mistune.

To boost the performance further, it is suggested to use PyPy with mistletoe.
Benchmark results show that on PyPy, mistletoe is about **twice as fast** as
mistune:

```sh
$ pypy3 test/benchmark.py mistune mistletoe
Test document: test/samples/syntax.md
Test iterations: 1000
Running tests with mistune, mistletoe...
========================================
mistune: 13.524028996936977
mistletoe: 6.477352762129158
```

The above result was achieved on PyPy 5.8.0-beta0, on a 13-inch Retina MacBook
Pro (Early 2015).

Developer's Guide
-----------------
Here's an example to add GitHub-style wiki links to the parsing process,
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
    def __init__(self, match_obj):
        pass
```

For spiritual guidance on regexes, refer to [xkcd][xkcd] classics. For an
actual representation of this author parsing Markdown with regexes, refer
to this brilliant [meme][meme] by [Greg Hendershott][hendershott].

mistletoe's span-level tokenizer will search for our pattern. When it finds
a match, it will pass in the match object as argument into our constructor.
We have defined our regex so that the first match group is the alternative
text, and the second one is the link target.

Note that alternative text can also contain other span-level tokens.  For
example, `[[*alt*|link]]` is a GitHub link with an `Emphasis` token as its
child.  To parse child tokens, simply pass `match_obj` to the `super`
constructor (which assumes children to be in `match_obj.group(1)`),
and save off all the additional attributes we need:

```python
from mistletoe.span_token import SpanToken

class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")
    def __init__(self, match_obj):
        super().__init__(match_obj)
        self.target = match_obj.group(2)
```

There you go: a new token in 7 lines of code.

**New in version 0.3**: token constructors now accepts match objects, which
allows us to utilize match groups, instead of doing dirty string manipulations.

### A new renderer

Adding a custom token to the parsing process usually involves a lot
of nasty implementation details. Fortunately, mistletoe takes care
of most of them for you. Simply pass your custom token class to 
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

**New in version 0.4**: custom tokens are included in the parsing process
even when the renderer is initialized as a normal constructor (i.e. not as
a context manager). This is primarily for ease of use. Your custom tokens and
their render functions, however, won't be cleaned up, so be careful!

```python
from mistletoe import Document
from plugins.github_wiki import GithubWikiRenderer

with open('foo.md', 'r') as fin:
    with GithubWikiRenderer() as renderer:
        rendered = renderer.render(Document(fin))
```

For more info, take a look at the `base_renderer` module in mistletoe.
The docstrings might give you a more granular idea of customizing mistletoe
to your needs.

Why mistletoe?
--------------

For me, the question becomes: why not [mistune][mistune]? My original
motivation really has nothing to do with starting a competition. Here's a list
of reasons I created mistletoe in the first place:

* I am interested in a Markdown-to-LaTeX transpiler in Python.
* I want to write more Python. Specifically, I want to try out some bleeding
  edge features in Python 3.6, which, in turn, makes me love the language even
  more.
* I am stuck at home during summer vacation without an internship, which, in
  turn, makes me realize how much I love banging out software from scratch, all
  by myself. Also, global warming keeps me indoors.
* I have long wanted to write a static site generator, *from scratch,
  by myself.* One key piece of the puzzle is my own Markdown parser. "How hard
  could it be?" (well, quite a lot harder than I expected.)
* "For fun," says David Beasley.

Here's two things mistune inspired mistletoe to do:

* Markdown parsers should be fast, and other parser implementations in Python
  leaves much to be desired.
* A parser implementation for Markdown does not need to restrict itself to one
  flavor (or, "standard") of Markdown.

Here's two things mistletoe does differently from mistune:

* Per its [readme][mistune], mistune will always be a single-file script.
  mistletoe breaks its functionality into modules.
* mistune, as of now, can only render Markdown into HTML. It is relatively
  trivial to write a new renderer for mistletoe.
    - This might make mistletoe look a bit closer to [MobileDoc][mobiledoc],
      in that it gives simple Markdown additional power to deal with a variety
      of additional input and output demands.

The implications of these are quite profound, and there's no definite
this-is-better-than-that answer. Mistune is near perfect if one wants what
it provides: I have used mistune extensively in the past, and had a great
experience. If you want more control, however, give mistletoe a try.

Finally, to quote [Raymond Hettinger][hettinger]:

> If you make something successful, you don't have to make something else
> unsuccessful.

Messing around in Python and rebuilding tools that I personally use and love
is an immensely more rewarding experience than competition.

Copyright & License
-------------------
* mistletoe's logo uses artwork by Daniele De Santis, under
  [CC BY 3.0][cc-by].
* mistletoe is released under [MIT][license].

[build-badge]: https://img.shields.io/travis/miyuchina/mistletoe.svg?style=flat-square
[cover-badge]: https://img.shields.io/coveralls/miyuchina/mistletoe.svg?style=flat-square
[pypi-badge]: https://img.shields.io/pypi/v/mistletoe.svg?style=flat-square
[wheel-badge]: https://img.shields.io/pypi/wheel/mistletoe.svg?style=flat-square
[travis]: https://travis-ci.org/miyuchina/mistletoe
[coveralls]: https://coveralls.io/github/miyuchina/mistletoe?branch=master
[pypi]: https://pypi.python.org/pypi/mistletoe
[mistune]: https://github.com/lepture/mistune
[python-markdown]: https://github.com/waylan/Python-Markdown
[python-markdown2]: https://github.com/trentm/python-markdown2
[contributing]: CONTRIBUTING.md
[xkcd]: https://xkcd.com/208/
[meme]: http://www.greghendershott.com/img/grumpy-regexp-parser.png
[hendershott]: http://www.greghendershott.com/2013/11/markdown-parser-redesign.html
[mobiledoc]: https://github.com/bustle/mobiledoc-kit
[hettinger]: https://www.youtube.com/watch?v=voXVTjwnn-U
[cc-by]: https://creativecommons.org/licenses/by/3.0/us/
[license]: LICENSE
