import sys
import mistletoe


def main(args):
    filenames, renderer = _parse(args)
    if filenames:
        convert(filenames, renderer)
    else:
        interactive(renderer)


def convert(filenames, renderer):
    for filename in filenames:
        convert_file(filename, renderer)


def convert_file(filename, renderer):
    """
    Parse a Markdown file and dump the output to stdout.
    """
    try:
        with open(filename, 'r') as fin:
            rendered = mistletoe.markdown(fin, renderer)
            print(rendered, end='')
    except OSError:
        sys.exit('Cannot open file "{}".'.format(filename))


def interactive(renderer):
    """
    Parse user input, dump to stdout, rinse and repeat.
    Python REPL style.
    """
    _import_readline()
    _print_heading(renderer)
    contents = []
    more = False
    while True:
        try:
            prompt, more = ('... ', True) if more else ('>>> ', True)
            contents.append(input(prompt) + '\n')
        except EOFError:
            print('\n' + mistletoe.markdown(contents, renderer), end='')
            more = False
            contents = []
        except KeyboardInterrupt:
            print('\nExiting.')
            break


def _parse(args):
    flag = None
    filenames = []
    renderer = mistletoe.HTMLRenderer
    for arg in args:
        if flag == 'renderer':
            renderer = _import(arg)
            flag = None
        elif arg in ('-r', '--renderer'):
            flag = 'renderer'
        elif arg in ('-v', '--version'):
            print('mistletoe [version {}]'.format(mistletoe.__version__))
            sys.exit(0)
        else:
            filenames.append(arg)
    if flag:
        print('[warning] unspecified flag: "{}". Ignoring.'.format(flag))
    return filenames, renderer


def _import(arg):
    import importlib
    *path, cls_name = arg.split('.')
    path = '.'.join(path)
    try:
        module = importlib.import_module(path)
        return getattr(module, cls_name)
    except ValueError:
        sys.exit('Please supply full path to your custom renderer.')
    except ImportError:
        sys.exit('Cannot import module "{}".'.format(path))
    except AttributeError:
        sys.exit('Cannot find renderer "{}" from module "{}".'.format(cls_name, path))


def _import_readline():
    try:
        import readline
    except ImportError:
        print('[warning] readline library not available.')


def _print_heading(renderer):
    print('mistletoe [version {}] (interactive)'.format(mistletoe.__version__))
    print('Type Ctrl-D to complete input, or Ctrl-C to exit.')
    if renderer is not mistletoe.HTMLRenderer:
        print('Using renderer: {}'.format(renderer.__name__))
