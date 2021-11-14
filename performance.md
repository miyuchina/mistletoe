<h1>Performance<img src='https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg' align='right' width='128' height='128'></h1>

mistletoe is the fastest CommonMark compliant implementation in Python,
even though since 2017 when the first benchmarks were run,
the competing implementations improved their performance notably.

The benchmark
-------------

Try the benchmarks yourself by running:

```sh
$ python3 test/benchmark.py  # all results in seconds
Test document: test/samples/syntax.md
Test iterations: 1000
Running tests with markdown, mistune, commonmark, mistletoe...
==============================================================
markdown: 36,1091867333333    # v3.3.4 from Feb 24, 2021
mistune: 10,7586129666667     # v0.8.4 from Oct 30, 2019
commonmark: 43,4187382666667  # v0.9.1 from Oct 04, 2019
mistletoe: 33,2067990666667   # v0.8.0 from Oct 09, 2021
# run with Python 3.7.5 on MS Windows 10
```

We notice that Mistune is the fastest Markdown parser,
and by a good margin, which demands some explanation.
mistletoe's biggest performance penalty
comes from stringently following the CommonMark spec,
which outlines a highly context-sensitive grammar for Markdown.
Mistune takes a simpler approach to the lexing and parsing process,
but this means that it cannot handle more complex cases,
e.g., precedence of different types of tokens, escaping rules, etc.

To see why this might be important to you,
consider the following Markdown input
([example 392][example-392] from the CommonMark spec):

```markdown
***foo** bar*
```

The natural interpretation is:

```html
<p><em><strong>foo</strong> bar</em></p>
```

... and it is indeed the output of Python-Markdown, Commonmark-py and mistletoe.
Mistune (version 0.8.3) greedily parses the first two asterisks
in the first delimiter run as a strong-emphasis opener,
the second delimiter run as its closer,
but does not know what to do with the remaining asterisk in between:

```html
<p><strong>*foo</strong> bar*</p>
```

The implication of this runs deeper,
and it is not simply a matter of dogmatically following an external spec.
By adopting a more flexible parsing algorithm,
mistletoe allows us to specify a precedence level to each token class,
including custom ones that you might write in the future.
Code spans, for example, has a higher precedence level than emphasis,
so

```markdown
*foo `bar* baz`
```

... is parsed as:

```html
<p>*foo <code>bar* baz</code></p>
```

... whereas Mistune parses this as:

```html
<p><em>foo `bar</em> baz`</p>
```

Of course, it is not *impossible* for Mistune to modify its behavior,
and parse these two examples correctly,
through more sophisticated regexes or some other means.
It is nevertheless *highly likely* that,
when Mistune implements all the necessary context checks,
it will suffer from the same performance penalties.

Contextual analysis is why the other implementations are slower.
The lack thereof is the reason mistune enjoys stellar performance
among similar parser implementations,
as well as the limitations that come with these performance benefits.

If you want an implementation that focuses on raw speed,
mistune remains a solid choice.
If you need a spec-compliant and readily extensible implementation, however,
mistletoe is still marginally faster than Python-Markdown,
and significantly faster than CommonMark-py.

Use PyPy for better performance
-------------------------------

Another bottleneck of mistletoe compared to mistune
is the function overhead. Because, unlike mistune, mistletoe chooses to split
functionality into modules, function lookups can take significantly longer than
mistune. To boost the performance further, it is suggested to use PyPy with mistletoe.
Benchmark results show that on PyPy, mistletoe's performance improves significantly:

```sh
$ pypy3 test/benchmark.py mistune mistletoe
Test document: test/samples/syntax.md
Test iterations: 1000
Running tests with mistune, mistletoe...
========================================
mistune: 9.720779
mistletoe: 21.984181399999997
# run with PyPy 3.7-v7.3.7 on MS Windows 10
```

[example-392]: https://spec.commonmark.org/0.28/#example-392
