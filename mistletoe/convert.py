import mistletoe


def convert(filename):
    """
    Parse a Markdown file and dump the output to stdout.
    """
    with open(filename, 'r') as fin:
        rendered = mistletoe.markdown(fin)    # default settings
    print(rendered, end='')                   # suppress trailing empty line
