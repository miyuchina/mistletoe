import sys
import mistletoe


def interactive():
    """
    Parse user input, dump to stdout, rinse and repeat.
    Python REPL style.
    """
    _import_readline()
    _print_heading()
    contents = []
    more = False
    while True:
        try:
            prompt, more = ('... ', True) if more else ('>>> ', True)
            contents.append(input(prompt) + '\n')
        except EOFError:
            print('\n' + mistletoe.markdown(contents), end='')
            more = False
            contents.clear()
        except KeyboardInterrupt:
            print('\nExiting.')
            break


def _import_readline():
    try:
        import readline
    except ImportError:
        print('[warning] readline library not available.')


def _print_heading():
    print('mistletoe [version {}] (interactive)'.format(mistletoe.__version__))
    print('Type Ctrl-D to complete input, or Ctrl-C to exit.')
