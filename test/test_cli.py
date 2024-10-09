from unittest import TestCase
from unittest.mock import call, patch, sentinel, mock_open, Mock
from mistletoe import cli


class TestCli(TestCase):
    @patch('mistletoe.cli.parse', return_value=Mock(filenames=[], renderer=sentinel.Renderer))
    @patch('mistletoe.cli.interactive')
    def test_main_to_interactive(self, mock_interactive, mock_parse):
        cli.main(None)
        mock_interactive.assert_called_with(sentinel.Renderer)

    @patch('mistletoe.cli.parse', return_value=Mock(filenames=['foo.md'], renderer=sentinel.Renderer))
    @patch('mistletoe.cli.convert')
    def test_main_to_convert(self, mock_convert, mock_parse):
        cli.main(None)
        mock_convert.assert_called_with(['foo.md'], sentinel.Renderer)

    @patch('importlib.import_module', return_value=Mock(Renderer=sentinel.RendererCls))
    def test_parse_renderer(self, mock_import_module):
        namespace = cli.parse(['-r', 'foo.Renderer'])
        mock_import_module.assert_called_with('foo')
        self.assertEqual(namespace.renderer, sentinel.RendererCls)

    def test_parse_filenames(self):
        filenames = ['foo.md', 'bar.md']
        namespace = cli.parse(filenames)
        self.assertEqual(namespace.filenames, filenames)

    @patch('mistletoe.cli.convert_file')
    def test_convert(self, mock_convert_file):
        filenames = ['foo', 'bar']
        cli.convert(filenames, sentinel.RendererCls)
        calls = [call(filename, sentinel.RendererCls) for filename in filenames]
        mock_convert_file.assert_has_calls(calls)

    @patch('mistletoe.markdown', return_value='rendered text')
    @patch('sys.stdout.buffer.write')
    @patch('builtins.open', new_callable=mock_open)
    def test_convert_file_success(self, mock_open_, mock_write, mock_markdown):
        filename = 'foo'
        cli.convert_file(filename, sentinel.RendererCls)
        mock_open_.assert_called_with(filename, 'r', encoding='utf-8')
        mock_write.assert_called_with('rendered text'.encode())

    @patch('builtins.open', side_effect=OSError)
    @patch('sys.exit')
    def test_convert_file_fail(self, mock_exit, mock_open_):
        filename = 'foo'
        cli.convert_file(filename, sentinel.RendererCls)
        mock_open_.assert_called_with(filename, 'r', encoding='utf-8')
        mock_exit.assert_called_with('Cannot open file "foo".')

    @patch('mistletoe.cli._import_readline')
    @patch('mistletoe.cli._print_heading')
    @patch('mistletoe.markdown', return_value='rendered text')
    @patch('builtins.print')
    def test_interactive(self, mock_print, mock_markdown,
                         mock_print_heading, mock_import_readline):
        def MockInputFactory(return_values):
            _counter = -1

            def mock_input(prompt=''):
                nonlocal _counter
                _counter += 1
                if _counter < len(return_values):
                    return return_values[_counter]
                elif _counter == len(return_values):
                    raise EOFError
                else:
                    raise KeyboardInterrupt
            return mock_input

        return_values = ['foo', 'bar', 'baz']
        with patch('builtins.input', MockInputFactory(return_values)):
            cli.interactive(sentinel.RendererCls)

        mock_import_readline.assert_called_with()
        mock_print_heading.assert_called_with(sentinel.RendererCls)
        mock_markdown.assert_called_with(['foo\n', 'bar\n', 'baz\n'],
                sentinel.RendererCls)
        calls = [call('\nrendered text', end=''), call('\nExiting.')]
        mock_print.assert_has_calls(calls)

    @patch('importlib.import_module', return_value=Mock(Renderer=sentinel.RendererCls))
    def test_import_success(self, mock_import_module):
        self.assertEqual(sentinel.RendererCls, cli._import('foo.Renderer'))

    @patch('sys.exit')
    def test_import_incomplete_path(self, mock_exit):
        cli._import('foo')
        error_msg = '[error] please supply full path to your custom renderer.'
        mock_exit.assert_called_with(error_msg)

    @patch('importlib.import_module', side_effect=ImportError)
    @patch('sys.exit')
    def test_import_module_error(self, mock_exit, mock_import_module):
        cli._import('foo.Renderer')
        mock_exit.assert_called_with('[error] cannot import module "foo".')

    @patch('importlib.import_module', return_value=Mock(spec=[]))
    @patch('sys.exit')
    def test_import_class_error(self, mock_exit, mock_import_module):
        cli._import('foo.Renderer')
        error_msg = '[error] cannot find renderer "Renderer" from module "foo".'
        mock_exit.assert_called_with(error_msg)

    @patch('builtins.__import__')
    @patch('builtins.print')
    def test_import_readline_success(self, mock_print, mock_import):
        cli._import_readline()
        mock_print.assert_not_called()

    @patch('builtins.__import__', side_effect=ImportError)
    @patch('builtins.print')
    def test_import_readline_fail(self, mock_print, mock_import):
        cli._import_readline()
        mock_print.assert_called_with('[warning] readline library not available.')

    @patch('builtins.print')
    def test_print_heading(self, mock_print):
        cli._print_heading(Mock(__name__='Renderer'))
        version = cli.mistletoe.__version__
        msgs = ['mistletoe [version {}] (interactive)'.format(version),
                'Type Ctrl-D to complete input, or Ctrl-C to exit.',
                'Using renderer: Renderer']
        calls = [call(msg) for msg in msgs]
        mock_print.assert_has_calls(calls)
