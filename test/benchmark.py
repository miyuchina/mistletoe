#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from importlib import import_module
from time import perf_counter


TEST_FILE = 'test/samples/syntax.md'
TIMES = 1000


def benchmark(package_name):
    def decorator(func):
        def inner():
            try:
                package = import_module(package_name)
            except ImportError:
                return 'not available.'

            start = perf_counter()
            for i in range(TIMES):
                func(package)
            end = perf_counter()

            return end - start
        return inner
    return decorator


@benchmark('markdown')
def run_markdown(package):
    with open(TEST_FILE, 'r', encoding='utf-8') as fin:
        return package.markdown(fin.read(), extensions=['fenced_code', 'tables'])


@benchmark('mistune')
def run_mistune(package):
    with open(TEST_FILE, 'r', encoding='utf-8') as fin:
        return package.markdown(fin.read())


@benchmark('commonmark')
def run_commonmark(package):
    with open(TEST_FILE, 'r', encoding='utf-8') as fin:
        return package.commonmark(fin.read())


@benchmark('mistletoe')
def run_mistletoe(package):
    with open(TEST_FILE, 'r', encoding='utf-8') as fin:
        return package.markdown(fin)


def run(package_name):
    print(package_name, end=': ')
    print(globals()['run_{}'.format(package_name.lower())]())


def run_all(package_names):
    prompt = 'Running tests with {}...'.format(', '.join(package_names))
    print(prompt)
    print('=' * len(prompt))
    for package_name in package_names:
        run(package_name)


def main(*args):
    print('Test document: {}'.format(TEST_FILE))
    print('Test iterations: {}'.format(TIMES))
    if args[1:]:
        run_all(args[1:])
    else:
        run_all(['markdown', 'mistune', 'commonmark', 'mistletoe'])


if __name__ == '__main__':
    main(*sys.argv)
