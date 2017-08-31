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
    print('mistletoe [version {}] (interactive)'.format(mistletoe.__version__))
    print('Type Ctrl-D to complete input, or Ctrl-C to exit.')
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
