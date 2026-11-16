"""Compatibility checks for the token children property."""
import unittest

from mistletoe.span_token import RawText
from mistletoe.token import Token


class TestTokenChildren(unittest.TestCase):
    def test_leaf_and_uninitialized(self):
        self.assertIsNone(Token().children)
        self.assertIsNone(RawText('leaf').children)
        self.assertIsNone(Token().parent)

    def test_collection_identity_and_parents(self):
        for collection_type in (list, tuple):
            with self.subTest(collection_type=collection_type):
                parent = Token()
                child = RawText('child')
                children = collection_type([child])
                parent.children = children
                self.assertIs(parent.children, children)
                self.assertIs(child.parent, parent)
                empty = collection_type()
                parent.children = empty
                self.assertIs(parent.children, empty)
                self.assertIs(child.parent, parent)

    def test_generator_is_stored_and_consumed(self):
        parent = Token()
        child = RawText('child')
        children = (item for item in [child])
        parent.children = children
        self.assertIs(parent.children, children)
        self.assertEqual(list(children), [])
        self.assertIs(child.parent, parent)
        with self.assertRaises(TypeError):
            repr(parent)

    def test_reassignment_and_later_mutation(self):
        first, second = Token(), Token()
        child, appended = RawText('child'), RawText('appended')
        children = [child]
        first.children = children
        second.children = [child]
        self.assertIs(child.parent, second)
        self.assertIs(first.children[0], child)
        children.append(appended)
        self.assertIsNone(appended.parent)
        first.children = None
        self.assertIsNone(first.children)
        self.assertIs(child.parent, second)
