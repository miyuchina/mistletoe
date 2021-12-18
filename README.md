<h1>mistletoe<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right' width='128' height='128'></h1>

[![Build Status][build-badge]][travis]
[![Coverage Status][cover-badge]][coveralls]
[![PyPI][pypi-badge]][pypi]
[![is wheel][wheel-badge]][pypi]

mistletoe is a Markdown parser in pure Python,
designed to be fast, spec-compliant and fully customizable.

Apart from being the fastest
CommonMark-compliant Markdown parser implementation in pure Python,
mistletoe also supports easy definitions of custom tokens.
Parsing Markdown into an abstract syntax tree
also allows us to swap out renderers for different output formats,
without touching any of the core components.

Remember to spell mistletoe in lowercase!

Features
--------
* **Fast**:
  mistletoe is the fastest implementation of CommonMark in Python.
  See the [performance][performance] section for details.

* **Spec-compliant**:
  CommonMark is [a useful, high-quality project][oilshell].
  mistletoe follows the [CommonMark specification][commonmark]
  to resolve ambiguities during parsing.
  Outputs are predictable and well-defined.

* **Extensible**:
  Strikethrough and tables are supported natively,
  and custom block-level and span-level tokens can easily be added.
  Writing a new renderer for mistletoe is a relatively
  trivial task.
  
  You can even write [a Lisp][scheme] in it.
  
Output formats
--------------

Renderers for the following "core" output formats exist within the mistletoe
module itself:

* HTML
* LaTeX
* AST (Abstract Syntax Tree; handy for debugging the parsing process)

Renderers for the following output formats are placed
in the [contrib][contrib] folder:

* HTML with MathJax (_mathjax.py_)
* HTML with code highlighting (using Pygments) (_pygments\_renderer.py_)
* HTML with TOC (for programmatical use) (_toc\_renderer.py_)
* HTML with support for GitHub wiki links (_github\_wiki.py_)
* Jira Markdown (_jira\_renderer.py_)
* XWiki Syntax (_xwiki20\_renderer.py_)
* Scheme (_scheme.py_)

Installation
------------
mistletoe is tested for Python 3.3 and above. Install mistletoe with pip:

```sh
pip3 install mistletoe
```

Alternatively, clone the repo:

```sh
git clone https://github.com/miyuchina/mistletoe.git
cd mistletoe
pip3 install -e .
```

This installs mistletoe in "editable" mode (because of the `-e` option).
That means that any changes made to the source code will get visible
immediately - that's because Python only makes a link to the specified
directory (`.`) instead of copying the files to the standard packages
folder.

See the [contributing][contributing] doc for how to contribute to mistletoe.

Usage
-----

### Usage from Python

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
process. The result should be equal to the output obtained from
the first example above.

```python
from mistletoe import Document, HTMLRenderer

with open('foo.md', 'r') as fin:
    with HTMLRenderer() as renderer:
        rendered = renderer.render(Document(fin))
```

**Important**: The parsing phase is currently tightly connected with initiation
and closing of a renderer. Therefore, you should never call `Document(...)`
outside of a `with ... as renderer` block, unless you know what you are doing.

### Usage from command-line

pip installation enables mistletoe's command-line utility. Type the following
directly into your shell:

```sh
mistletoe foo.md
```

This will transpile `foo.md` into HTML, and dump the output to stdout. To save
the HTML, direct the output into a file:

```sh
mistletoe foo.md > out.html
```

You can use a different renderer by including the full path to the renderer
class after a `-r` or `--renderer` flag. For example, to transpile into
LaTeX:

```sh
mistletoe foo.md --renderer mistletoe.latex_renderer.LaTeXRenderer
```

Note: The renderers inside the `contrib` directory are not currently a part of
the `mistletoe` module when mistletoe is installed as a regular package.
So if you want to use a renderer from the `contrib` directory, you either
have to add that directory to Python's [PYTHONPATH][pythonpath]
or install mistletoe with the `-e` switch (see [Installation](#installation)).

### mistletoe interactive mode

Running `mistletoe` without specifying a file will land you in interactive
mode.  Like Python's REPL, interactive mode allows you to test how your
Markdown will be interpreted by mistletoe:

```html
mistletoe [version 0.7.2] (interactive)
Type Ctrl-D to complete input, or Ctrl-C to exit.
>>> some **bold** text
... and some *italics*
...
<p>some <strong>bold</strong> text
and some <em>italics</em></p>
>>>
```

The interactive mode also accepts the `--renderer` flag:

```latex
mistletoe [version 0.7.2] (interactive)
Type Ctrl-D to complete input, or Ctrl-C to exit.
Using renderer: LaTeXRenderer
>>> some **bold** text
... and some *italics*
...
\documentclass{article}
\begin{document}

some \textbf{bold} text
and some \textit{italics}
\end{document}
>>>
```

Who uses mistletoe?
-------------------

mistletoe is used by projects of various target audience.
You can find some concrete projects in the "Used by" section
on [Libraries.io][libraries-mistletoe], but this is definitely not a complete
list.

### Run mistletoe from CopyQ

One notable example is running mistletoe as a Markdown converter from the
advanced clipboard manager called [CopyQ][copyq]. One just needs to install
the [Convert Markdown to ...][copyq-convert-md] custom script command
and then run this command on any selected Markdown text.

Why mistletoe?
--------------

"For fun," says David Beazley.

Further reading
---------------

* [Performance][performance]
* [Developer's Guide](dev-guide.md)

Copyright & License
-------------------
* mistletoe's logo uses artwork by [Freepik][icon], under
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
[commonmark-py]: https://github.com/rtfd/CommonMark-py
[performance]: performance.md
[oilshell]: https://www.oilshell.org/blog/2018/02/14.html
[commonmark]: https://spec.commonmark.org/
[contrib]: https://github.com/miyuchina/mistletoe/tree/master/contrib
[scheme]: https://github.com/miyuchina/mistletoe/blob/dev/contrib/scheme.py
[contributing]: CONTRIBUTING.md
[icon]: https://www.freepik.com
[cc-by]: https://creativecommons.org/licenses/by/3.0/us/
[license]: LICENSE
[pythonpath]: https://stackoverflow.com/questions/16107526/how-to-flexibly-change-pythonpath
[libraries-mistletoe]: https://libraries.io/pypi/mistletoe
[copyq]: https://hluk.github.io/CopyQ/
[copyq-convert-md]: https://github.com/hluk/copyq-commands/tree/master/Global#convert-markdown-to-
