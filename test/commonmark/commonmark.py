import re
import sys
import json
from mistletoe import markdown
from traceback import print_tb
from argparse import ArgumentParser


def run_tests(test_entries, start=None, end=None, quiet=False, verbose=False):
    start = start or 0
    end = end or sys.maxsize
    results = [run_test(test_entry, quiet) for test_entry in test_entries
            if test_entry['example'] >= start and test_entry['example'] <= end]
    if not quiet:
        print('=' * 80)
    if verbose:
        print_failure_in_sections(results)
    print('failed:', len(list(filter(lambda x: not x[0], results))))
    print(' total:', len(results))


def run_test(test_entry, quiet=False):
    test_case = test_entry['markdown'].splitlines(keepends=True)
    try:
        output = markdown(test_case)
        success = compare(test_entry['html'].replace('\t', '    '), output)
        if not success and not quiet:
            print_test_entry(test_entry, output)
        return success, test_entry['section']
    except Exception as exception:
        if not quiet:
            print_exception(exception, test_entry)
        return False, test_entry['section']


def load_tests(specfile):
    with open(specfile, 'r') as fin:
        return json.load(fin)


def locate_section(section, tests):
    start = None
    end = None
    for test in tests:
        if re.search(section, test['section'], re.IGNORECASE):
            if start is None:
                start = test['example']
        elif start is not None and end is None:
            end = test['example'] - 1
            return start, end
    raise RuntimeError("Section '{}' not found, aborting.".format(section))


def compare(expected, output):
    return expected == output.replace('&#x27;', '\'')


def print_exception(exception, test_entry):
    print_test_entry(test_entry, '-- exception --', fout=sys.stderr)
    print(exception.__class__.__name__ + ':', exception, file=sys.stderr)
    print('Traceback: ', file=sys.stderr)
    print_tb(exception.__traceback__)


def print_test_entry(test_entry, output, fout=sys.stdout):
    print('example: ', repr(test_entry['example']), file=fout)
    print('markdown:', repr(test_entry['markdown']), file=fout)
    print('html:    ', repr(test_entry['html']), file=fout)
    print('output:  ', repr(output), file=fout)
    print(file=fout)



def print_failure_in_sections(results):
    section = results[0][1]
    failed = 0
    total = 0
    for result in results:
        if section != result[1]:
            if failed:
                section_str = "Failed in section '{}':".format(section)
                result_str = "{:>3} / {:>3}".format(failed, total)
                print('{:70} {}'.format(section_str, result_str))
            section = result[1]
            failed = 0
            total = 0
        if not result[0]:
            failed += 1
        total += 1
    if failed:
        section_str = "Failed in section '{}':".format(section)
        result_str = "{:>3} / {:>3}".format(failed, total)
        print('{:70} {}'.format(section_str, result_str))
    print()


def main():
    parser = ArgumentParser(description="Custom script for running Commonmark tests.")
    parser.add_argument('start', type=int, nargs='?', default=None,
                        help="Run tests starting from this position.")
    parser.add_argument('end', type=int, nargs='?', default=None,
                        help="Run tests until this position.")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help="Output failure count in every section.")
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help="Suppress failed test entry output.")
    parser.add_argument('-s', '--section', dest='section', default=None,
                        help="Only run tests in specified section.")
    parser.add_argument('-f', '--file', dest='tests', type=load_tests,
                        default='test/commonmark/commonmark.json',
                        help="Specify alternative specfile to run.")
    args = parser.parse_args()

    start   = args.start
    end     = args.end
    verbose = args.verbose
    quiet   = args.quiet
    tests   = args.tests
    if args.section is not None:
        start, end = locate_section(args.section, tests)

    run_tests(tests, start, end, quiet, verbose)


if __name__ == '__main__':
    main()

