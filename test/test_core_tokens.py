from unittest import TestCase
from mistletoe.core_tokens import (MatchObj, Delimiter, follows, shift_whitespace,
        is_control_char, deactivate_delimiters, preceded_by, succeeded_by)


class TestCoreTokens(TestCase):
    def test_match_obj(self):
        match = MatchObj(0, 2, (0, 1, 'a'), (1, 2, 'b'))
        self.assertEqual(match.start(), 0)
        self.assertEqual(match.start(1), 0)
        self.assertEqual(match.start(2), 1)
        self.assertEqual(match.end(), 2)
        self.assertEqual(match.end(1), 1)
        self.assertEqual(match.end(2), 2)
        self.assertEqual(match.group(), 'ab')
        self.assertEqual(match.group(1), 'a')
        self.assertEqual(match.group(2), 'b')

    def test_delimiter(self):
        delimiter = Delimiter(4, 6, 'abcd**')
        self.assertEqual(delimiter.type, '**')
        self.assertEqual(delimiter.number, 2)
        self.assertEqual(delimiter.active, True)
        self.assertEqual(delimiter.start, 4)
        self.assertEqual(delimiter.end, 6)

    def test_delimiter_remove_left(self):
        delimiter = Delimiter(4, 6, 'abcd**')
        self.assertTrue(delimiter.remove(1, left=True))
        self.assertEqual(delimiter.number, 1)
        self.assertEqual(delimiter.start, 5)
        self.assertEqual(delimiter.end, 6)

    def test_delimiter_remove_right(self):
        delimiter = Delimiter(4, 6, 'abcd**')
        self.assertTrue(delimiter.remove(1, left=False))
        self.assertEqual(delimiter.number, 1)
        self.assertEqual(delimiter.start, 4)
        self.assertEqual(delimiter.end, 5)

    def test_delimiter_remove_empty(self):
        delimiter = Delimiter(4, 6, 'abcd**')
        self.assertFalse(delimiter.remove(2))

    def test_follows(self):
        string = '(foobar)'
        self.assertTrue(follows(string, 6, ')'))
        self.assertFalse(follows(string, 6, '('))
        self.assertFalse(follows(string, 7, ')'))

    def test_shift_whitespace(self):
        string = ' \n\t\rfoo'
        self.assertEqual(shift_whitespace(string, 0), 4)
        self.assertEqual(shift_whitespace('', 0), 0)

    def test_is_control_char(self):
        char = chr(0)
        self.assertTrue(is_control_char(char))
        self.assertFalse(is_control_char('a'))

    def test_deactivate_delimiters(self):
        s = 'abc'
        delimiters = [Delimiter(0, 1, s), Delimiter(1, 2, s), Delimiter(2, 3, s)]
        deactivate_delimiters(delimiters, 2, 'b')
        self.assertTrue(delimiters[0].active)
        self.assertFalse(delimiters[1].active)
        self.assertTrue(delimiters[2].active)

    def test_preceded_by(self):
        whitespace = ' \t\n\r'
        self.assertTrue(preceded_by(1, ' abc', whitespace))
        self.assertTrue(preceded_by(0, 'aabc', whitespace))
        self.assertFalse(preceded_by(1, 'aabc', whitespace))
        self.assertFalse(preceded_by(0, 'aabc', 'abc'))

    def test_succeeded_by(self):
        whitespace = ' \t\n\r'
        self.assertTrue(succeeded_by(3, 'abc ', whitespace))
        self.assertTrue(succeeded_by(4, 'abcc', whitespace))
        self.assertFalse(succeeded_by(3, 'abcc', whitespace))
        self.assertFalse(succeeded_by(4, 'abcc', 'abc'))
