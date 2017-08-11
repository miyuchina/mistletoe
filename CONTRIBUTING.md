<h1>Contributing<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right'></h1>

You've seen mistletoe: it branches off in all directions, bringing people
together. We would love to see what you can make of mistletoe, which direction
you would take it to. Or maybe you can discover some [Nargles][nargles], which,
by the way, totally exists.

The following instructions serve as guidelines, and you should use your best
judgements when employing them.

## Getting started

Refer to the [README][readme] for install instructions. Since you're going to
mess with the code, it's prefered that you clone the repo directly.

Check back on the dev branch regularly to avoid redoing work that others might
have done. The master branch is updated only when features on the dev branch
are stabilized somewhat.

## Things you can do

### Introducing new features

It is suggested that you **open an issue first** before working on new
features. Include your reasons, use case, and maybe plans for implementation.
That way, we have a better idea of what you'll be working on, and can hopefully
avoid collision. Your pull request may also get merged much faster.

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

### Writing documentations

The creator might not the best person to write documentations; the users,
knowing all the painpoints, have a better idea of actual use cases and possible
things that can go wrong.

Go to the mistletoe [wiki][wiki] and write up your own topic. Alternatively,
write docstrings or comments for functions that are missing them. mistletoe
generally follows the [Google Python Style Guide][style-guide] to format
comments.

## Writing code

### Commit messages

* minimal cosmetic changes are fine to mix in with your commits, but try feel
  guilty when you do that, and if it's not too big of a hassle, break them
  into two commits.

* give clear, instructive commit messages. Try using phrases like "added XXX
  feature" or "fixed XXX (#42)".

* if you find yourself cramming too many things into one commit message, you
  should probably break them into multiple commits.

* emojis are awesome. Use them like this:

  | Emoji | Description                     |
  | :---: | :------------------------------ |
  |  📚   | Update documentation.           |
  |  🐎   | Performance improvements.       |
  |  💡   | New features.                   |
  |  🐛   | Bug fixes.                      |
  |  🚨   | Under construction.             |
  |  ☕️   | Refactoring / cosmetic changes. |
  |  🌎   | Internationalization.           |

### Style guide

Here's the obligatory [PEP8][pep-8] link, but here's a much shorter list of
things to be aware of:

* mistletoe uses `CamelCase` for classnames, `snake_case` for functions and
  methods;
* mistletoe uses *one* blank line between classes and functions, even global
  ones, despite PEP8's suggestion to the contrary.
* mistletoe follows the eighty-character rule: if you find your line to be
  too lengthy, try giving variable names to expressions, and break it up
  that way. That said, it's okay to go over the charater limit occasionally.
* mistletoe uses four spaces instead of a tab to indent. For vim users,
  include `set ts=4 sw=4 ai et` in your `.vimrc`.

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
[email]: mailto:miyu.china@icloud.com
