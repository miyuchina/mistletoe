import sys
import mistletoe


def convert(args):
    filenames, renderer = _parse(args)
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
        else:
            filenames.append(arg)
    return filenames, renderer


def _import(arg):
    import importlib
    *path, cls_name = arg.split('.')
    path = '.'.join(path)
    try:
        module = importlib.import_module(path)
        renderer = getattr(module, cls_name)
    except ImportError:
        sys.exit('Cannot import module "{}".'.format(path))
    except AttributeError:
        sys.exit('Cannot find renderer "{}" from module "{}"'.format(cls_name, path))
    return renderer
