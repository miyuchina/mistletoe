"""
Make mistletoe runnable as a script with default settings.
"""

import sys
import mistletoe

def convert(filename):
    """
    Parse a Markdown file and dump the output to stdout.
    """
    with open(filename, 'r') as fin:
        rendered = mistletoe.markdown(fin)    # default settings
    print(rendered, end='')                   # suppress trailing empty line

def interactive():
    """
    Parse user input, dump to stdout, rinse and repeat.
    Python REPL style.
    """
    print('mistletoe [version 0.2] (interactive)')
    print('Type Ctrl-D to complete input, or Ctrl-C to exit.')
    while True:                               # eval loop
        try:
            contents = []
            print('>>> ', end='')
            while True:                       # input loop
                try:
                    line = input() + '\n'     # input() doesn't have '\n'
                except EOFError:              # user presses ^D
                    break
                contents.append(line)
                print('... ', end='')
            print('\n' + mistletoe.markdown(contents), end='')  # dump output
        except KeyboardInterrupt:             # user presses ^C
            print('\nExiting.')
            return

def main():
    """
    Entry point. Select mode based on len(sys.argv).
    """
    if len(sys.argv) > 1:
        convert(sys.argv[1])
    else:
        interactive()

if __name__ == "__main__":
    main()
