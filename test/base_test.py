"""
Base classes for tests.
"""

from unittest import TestCase
from mistletoe.block_token import Document


class BaseRendererTest(TestCase):
    """
    Base class for tests of renderers.
    """
    def setUp(self):
        self.maxDiff = None

    def markdownResultTest(self, markdown, expected):
        output = self.renderer.render(Document(markdown))
        self.assertEqual(output, expected)

    def filesBasedTest(func):
        """
        Note: Use this as a decorator on a test function with an empty body.
        This is a realization of the "convention over configuration"
        practice. You only need to define a unique ``sampleOutputExtension`` within your
        test case setup, in addition to the ``renderer`` under the test of course.

        Runs the current renderer against input parsed from a file and
        asserts that the renderer output is equal to content stored in another file.
        Both the "input" and "expected output" files need to have the same ``filename``
        that is extracted from the decorated test function name.
        """
        def wrapper(self):
            # take the string after the last '__' in function name
            filename = func.__name__
            filename = filename.split('__', 1)[1]

            # parse input markdown, call render on it and check the output
            with open('test/samples/{}.md'.format(filename), 'r') as fin:
                output = self.renderer.render(Document(fin))

                with open('test/samples/{}.{}'.format(filename, self.sampleOutputExtension), 'r') as expectedFin:
                    expected = ''.join(expectedFin)

                self.assertEqual(output, expected)
        return wrapper
