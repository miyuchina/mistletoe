import sys
import mistletoe


def convert(*filenames):
    """
    Parse all files in filenames.
    """
    for filename in filenames:
        convert_file(filename)


def convert_file(filename):
    """
    Parse a Markdown file and dump the output to stdout.
    """
    try:
        with open(filename, 'r') as fin:
            rendered = mistletoe.markdown(fin)
            print(rendered, end='')
    except OSError:
        sys.exit('Cannot open file "{}".'.format(filename))
