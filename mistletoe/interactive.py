import sys
import mistletoe

try:
    import readline
except ImportError:
    sys.stdout.write('[Warning] readline library not available.')


def interactive():
    """
    Parse user input, dump to stdout, rinse and repeat.
    Python REPL style.
    """
    if sys.stdout.isatty():
        print('\033[32;1mmistletoe\033[0m [version {}] '
              '(interactive)'.format(mistletoe.__version__))
        print('Type \033[1mCtrl-D\033[0m to complete input, '
              'or \033[1mCtrl-C\033[0m to exit.')
    contents = []
    more = False
    while True:
        try:
            if not more:
                prompt = '>>> '
                more = True
            else:
                prompt = '... '
            try:
                line = input(prompt) + '\n'
                contents.append(line)
            except EOFError:
                print('\n' + mistletoe.markdown(contents), end='')
                more = False
                contents.clear()
        except KeyboardInterrupt:
            print('\nExiting.')
            break
