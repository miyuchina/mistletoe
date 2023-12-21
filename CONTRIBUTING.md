<h1>Contributing<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right' width='128' height='128'></h1>

You've seen mistletoe: it branches off in all directions, bringing people
together. We would love to see what you can make of mistletoe, which direction
you would take it to. Or maybe you can discover some [Nargles][nargles], which,
by the way, totally exist.

The following instructions serve as guidelines, and you should use your best
judgement when employing them.

## Getting started

Refer to the [README][readme] for install instructions. Since you're going to
mess with the code, it's preferred that you clone the repo directly.

## Things you can do

### Introducing new features

It is suggested that you **open an issue first** before working on new
features. Include your reasons, use case, and maybe plans for implementation.
That way, we have a better idea of what you'll be working on, and can hopefully
avoid collision. Your pull request may also get merged much faster.

There is a contrib directory (and Python package) for software that has been
contributed to the project, but which isn't maintained by the core developers.
This is a good place to put things like renderers for new formats.

### Fixing bugs

Before you post an issue, try narrowing the problem down to the smallest
component possible. For example, if an `InlineCode` token is not parsed
correctly, include only the paragraph that introduce the error, not the
entire document.

You might find mistletoe's interactive mode handy when tracking down bugs.
Type in your input, and you immediately see how mistletoe handles it.
I created it just for this purpose. To use it, run `mistletoe` (or
`python3 mistletoe`) in your shell without arguments.

Markdown is a very finicky document format to parse, so if something does not
work as intended, it's probably my fault and not yours.

### Writing documentation

The creator might not the best person to write documentation; the users,
knowing all the painpoints, have a better idea of actual use cases and possible
things that can go wrong.

Write docstrings or comments for functions that are missing them. mistletoe
generally follows the [Google Python Style Guide][style-guide] to format
comments.

## Writing code

### Atomic commits

* minimal cosmetic changes are fine to mix in with your commits, but try feel
  guilty when you do that, and if it's not too big of a hassle, break them
  into two commits.

* similarly, provided there occur bigger, independent areas of changes you
  would like to address in a pull request, it may be a good idea to split
  your pull request into multiple ones.

### Commit messages

* give clear, instructive commit messages.
  [Conventional Commits](conv-commits) is the preferred way of how to
  structure a commit message.

* here is an example commit message when fixing some stuff from a numbered
  issue: `fix: avoid infinite loop when parsing specific Footnotes (#124)`.

* find 5 minutes of your time to add important non-obvious details
  to the message body, like WHY or HOW.
  This can tremendously reduce the time necessary to investigate future issues
  and to get better understanding of the project code for newbies.
  (Yet, this should not serve as a replacement for proper documentation or
  inline comments.)

### Style guide

Here's the obligatory [PEP8][pep-8] link, but here's a much shorter list of
things to be aware of:

* mistletoe uses `CamelCase` for classnames, `snake_case` for functions and
  methods;
* mistletoe follows the eighty-character rule: if you find your line to be
  too lengthy, try giving variable names to expressions, and break it up
  that way. That said, it's okay to go over the character limit occasionally.
* mistletoe uses four spaces instead of a tab to indent. For vim users,
  include `set ts=4 sw=4 ai et` in your `.vimrc`.
* recommended Python tooling:
    * [Black][black-formatter] as the code formatter
    * [flake8][flake8] as the linter (style checker)

Apart from that, stay consistent with the coding style around you. But don't
get boggled down by this: if you have a genius idea, I'd love to clean up
for you; write down your genius idea first.

## Get in touch

I tweet [@mi_before_yu][twitter]. Also yell at me over [email][email].

[nargles]: http://harrypotter.wikia.com/wiki/Nargle
[readme]: README.md
[wiki]: https://github.com/miyuchina/mistletoe/wiki
[style-guide]: https://google.github.io/styleguide/pyguide.html
[pep-8]: https://www.python.org/dev/peps/pep-0008/
[twitter]: https://twitter.com/mi_before_yu
[email]: mailto:hello@afteryu.me
[conv-commits]: https://www.conventionalcommits.org/
[black-formatter]: https://black.readthedocs.io/
[flake8]: https://flake8.pycqa.org/
