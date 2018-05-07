import sys
import json
import mistletoe
from pprint import pprint
from traceback import print_tb


def run_tests(test_entries, runnable, start=None, end=None):
    start = start or 0
    end = end or sys.maxsize
    return [run_test(test_entry, runnable) for test_entry in test_entries
            if test_entry['example'] >= start and test_entry['example'] < end]


def run_test(test_entry, runnable):
    test_case = test_entry['markdown'].splitlines(keepends=True)
    try:
        output = runnable(test_case)
        success = compare(test_entry['html'].replace('\t', '    '), output)
        if not success:
            print_test_entry(test_entry, 'html', 'markdown', 'example')
            print('output:', repr(output), '\n')
        return success
    except Exception as exception:
        print_exception(exception, test_entry)
        return False


def compare(expected, output):
    return ''.join(expected.splitlines()) == ''.join(output.splitlines())


def print_exception(exception, test_entry):
    print(exception.__class__.__name__ + ':', exception)
    print('\nTraceback: ')
    print_tb(exception.__traceback__)
    print_test_entry(test_entry)
    print('='*80)


def print_test_entry(test_entry, *keywords):
    if keywords:
        pprint({keyword: test_entry[keyword] for keyword in keywords})
    else:
        pprint(test_entry)


def main(start, end):
    with open('commonmark.json', 'r') as fin:
        test_entries = json.load(fin)
    return run_tests(test_entries, mistletoe.markdown, start, end)


if __name__ == '__main__':
    start, end = None, None
    if len(sys.argv) > 1:
        start = int(sys.argv[1])
    if len(sys.argv) > 2:
        end = int(sys.argv[2])
    results = main(start, end)
    print('failed:', len(list(filter(lambda x: not x, results))))
    print(' total:', len(results))

