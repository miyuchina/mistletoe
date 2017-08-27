import sys
import mistletoe


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
            sys.stdout.write(prompt)
            try:
                line = input() + '\n'
                contents.append(line)
            except EOFError:
                sys.stdout.write('\n' + mistletoe.markdown(contents))
                more = False
                contents.clear()
        except KeyboardInterrupt:
            sys.stdout.write('\nExiting.\n')
            break
