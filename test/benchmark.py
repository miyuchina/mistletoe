#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import markdown
import markdown2
import mistune
import mistletoe
from time import perf_counter

__all__ = ['run_markdown', 'run_markdown2', 'run_mistune', 'run_mistletoe']

TEST_FILE = 'test/samples/syntax.md'
TIMES = 1000

def benchmark(func):
    def inner():
        print(func.__name__.split('_')[1], end=": ")
        start = perf_counter()
        for i in range(TIMES):
            func()
        end = perf_counter()
        print(end - start)
    return inner

@benchmark
def run_markdown():
    with open(TEST_FILE, 'r') as fin:
        return markdown.markdown(fin.read(), ['extra'])

@benchmark
def run_markdown2():
    with open(TEST_FILE, 'r') as fin:
        extras = ['code-friendly', 'fenced-code-blocks', 'footnotes']
        return markdown2.markdown(fin.read(), extras=extras)

@benchmark
def run_mistune():
    with open(TEST_FILE, 'r') as fin:
        return mistune.markdown(fin.read())

@benchmark
def run_mistletoe():
    with open(TEST_FILE, 'r') as fin:
        return mistletoe.markdown(fin)

def main(*args):
    print('Test document: {}'.format(TEST_FILE))
    print('Test iterations: {}'.format(TIMES))
    if args[1:]:
        runnables = ['run_{}'.format(arg) for arg in args[1:]]
        prompt = 'Running tests with {}...'.format(', '.join(args[1:]))
        print(prompt)
        print('='*len(prompt))
        for runnable in runnables:
            globals()[runnable]()
    else:
        packages = [key.split('_')[1] for key in __all__]
        prompt = 'Running tests with {}...'.format(', '.join(packages))
        print(prompt)
        print('='*len(prompt))
        for key in __all__:
            globals()[key]()

if __name__ == '__main__':
    main(*sys.argv)
