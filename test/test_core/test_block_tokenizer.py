import unittest
import core.block_tokenizer as tokenizer

class TestBlockTokenizer(unittest.TestCase):
    def test_read_quote(self):
        index = 0
        mixed_lines = ['> in the quote\n',
                       '> in the quote line 2\n',
                       'not in the quote\n'] # stops here
        pure_lines = ['> in the quote\n',
                      '> in the quote line 2\n',
                      '> still in the quote\n'] # stops here
        test_cases = mixed_lines, pure_lines
        test_outputs = 2, 3
        for test, output in zip(test_cases, test_outputs):
            with self.subTest(test=test):
                self.assertEqual(tokenizer.read_quote(index, test), output)

    def test_read_block_code(self):
        index = 0
        mixed_lines = ['```\n',
                       'rm -rf dir\n',
                       'mkdir hello\n',
                       '```\n',
                       'not in the code\n', # stops here
                       'nor this\n']
        pure_lines = ['```\n',
                      'rm -rf dir\n',
                      'mkdir hello\n',
                      'still in the code\n'] # stops here
        test_cases = mixed_lines, pure_lines
        test_outputs = 4, 4
        for test, output in zip(test_cases, test_outputs):
            with self.subTest(test=test):
                self.assertEqual(tokenizer.read_block_code(index, test), output)

    def test_read_paragraph(self):
        index = 0
        mixed_lines = ['\n',
                       'line 1\n',
                       'line 2\n',
                       '\n', # stops here
                       'not in the paragraph']
        pure_lines = ['\n',
                      'line 1\n'] # stops here
        test_cases = mixed_lines, pure_lines
        test_outputs = 3, 2
        for test, output in zip(test_cases, test_outputs):
            with self.subTest(test=test):
                self.assertEqual(tokenizer.read_paragraph(index, test), output)

    def test_read_list(self):
        index = 0
        inner_list = ['    - nested item 1',
                      '    - nested item 2',
                      '- item 1', # stops here
                      '- item 2']
        outer_list = ['- item 1',
                      '    - nested item 1',
                      '    - nested item 2',
                      '- item 2',
                      '- item 3'] # stops here
        test_cases = inner_list, outer_list
        test_outputs = 2, 5
        levels = 1, 0
        for test, output, level in zip(test_cases, test_outputs, levels):
            with self.subTest(test=test):
                self.assertEqual(tokenizer.read_list(index, test, level), output)
