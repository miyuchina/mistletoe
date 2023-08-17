#!/usr/bin/env python3
# Copyright 2018 Tile, Inc.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import sys
import getopt
import mistletoe
from mistletoe.contrib.jira_renderer import JiraRenderer

usageString = '%s <markdownfile>' % os.path.basename(sys.argv[0])
helpString = """
Convert Markdown (CommonMark) to JIRA wiki markup
-h, --help                        help
-v, --version                     version
-o <outfile>, --output=<outfile>  output file, use '-' for stdout (default: stdout)

If no input file is specified, stdin is used.
"""

"""
Command-line utility to convert Markdown (CommonMark) to JIRA markup.

JIRA markup spec: https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all
CommonMark spec: http://spec.commonmark.org/0.30/#introduction
"""


class CommandLineParser:
    def __init__(self):
        try:
            optlist, args = getopt.getopt(sys.argv[1:], 'hvo:',
                                          ['help',
                                           'version',
                                           'output='])

        except getopt.GetoptError as err:
            sys.stderr.write(err.msg + '\n')
            sys.stderr.write(usageString + '\n')
            sys.exit(1)

        app = MarkdownToJira()
        app.run(optlist, args)


class MarkdownToJira:
    def __init__(self):
        self.version = "1.0.2"
        self.options = {}
        self.options['output'] = '-'

    def run(self, optlist, args):

        for o, i in optlist:
            if o in ('-h', '--help'):
                sys.stderr.write(usageString + '\n')
                sys.stderr.write(helpString + '\n')
                sys.exit(1)

            elif o in ('-v', '--version'):
                sys.stdout.write('%s\n' % self.version)
                sys.exit(0)

            elif o in ('-o', '--output'):
                self.options['output'] = i

        if len(args) < 1:
            sys.stderr.write(usageString + '\n')
            sys.exit(1)

        with open(args[0], 'r', encoding='utf-8') if len(args) == 1 else sys.stdin as infile:
            rendered = mistletoe.markdown(infile, JiraRenderer)

        if self.options['output'] == '-':
            sys.stdout.write(rendered)
        else:
            with open(self.options['output'], 'w', encoding='utf-8') as outfile:
                outfile.write(rendered)


MarkdownToJIRA = MarkdownToJira
"""
Deprecated name of the `MarkdownToJira` class.
"""


if __name__ == '__main__':
    CommandLineParser()
