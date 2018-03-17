import sys
import mistletoe
from argparse import ArgumentParser


version_str = 'mistletoe [version {}]'.format(mistletoe.__version__)


def main(args):
    namespace = parse(args)
    if namespace.filenames:
        convert(namespace.filenames, namespace.renderer)
    else:
        interactive(namespace.renderer)


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


def parse(args):
    parser = ArgumentParser()
    parser.add_argument('-r', '--renderer', type=_import,
                        default='mistletoe.HTMLRenderer',
                        help='specify an importable renderer class')
    parser.add_argument('-v', '--version', action='version', version=version_str)
    parser.add_argument('filenames', nargs='*',
                        help='specify an optional list of files to convert')
    return parser.parse_args(args)


def _import(arg):
    import importlib
    try:
        cls_name, path = map(lambda s: s[::-1], arg[::-1].split('.', 1))
        module = importlib.import_module(path)
        return getattr(module, cls_name)
    except ValueError:
        sys.exit('[error] please supply full path to your custom renderer.')
    except ImportError:
        sys.exit('[error] cannot import module "{}".'.format(path))
    except AttributeError:
        sys.exit('[error] cannot find renderer "{}" from module "{}".'.format(cls_name, path))


def _import_readline():
    try:
        import readline
    except ImportError:
        print('[warning] readline library not available.')


def _print_heading(renderer):
    print('{} (interactive)'.format(version_str))
    print('Type Ctrl-D to complete input, or Ctrl-C to exit.')
    if renderer is not mistletoe.HTMLRenderer:
        print('Using renderer: {}'.format(renderer.__name__))

