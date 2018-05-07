SKIPPED_TESTS = {}


def run_tests(test_entries, runnable):
    return [run_test(test_entry, runnable) for test_entry in test_entries
            if test_entry['example'] not in SKIPPED_TESTS]


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


def compare(expected, output):
    return ''.join(expected.splitlines()) == ''.join(output.splitlines())


def print_exception(exception, test_entry):
    from traceback import print_tb
    print(exception.__class__.__name__ + ':', exception)
    print('\nTraceback: ')
    print_tb(exception.__traceback__)
    print_test_entry(test_entry)
    print('='*80)


def print_test_entry(test_entry, *keywords):
    from pprint import pprint
    if keywords:
        pprint({keyword: test_entry[keyword] for keyword in keywords})
    else:
        pprint(test_entry)


def main():
    import json
    import mistletoe
    with open('commonmark.json', 'r') as fin:
        test_entries = json.load(fin)
    return run_tests(test_entries, mistletoe.markdown)


if __name__ == '__main__':
    results = main()
    print('failed:', len(list(filter(lambda x: not x, results))))
    print(' total:', len(results))

