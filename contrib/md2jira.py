#!/usr/bin/env python3
# Copyright 2016

import os
import sys
import getopt
import subprocess
import shutil
import mistletoe
from plugins.jira_renderer import JIRARenderer

usageString = '%s <markdownfile>' % os.path.basename(sys.argv[0])
helpString = """
-h, --help                        help
-v, --version                     version
-o <outfile>, --output=<outfile>  output file, use '-' for stdout (default: stdout)
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

        app = MarkdownToJIRA()
        app.run(optlist, args)


class MarkdownToJIRA:
    def __init__(self):
        self.version = 1.0
        self.options = {}
        self.options['output'] = '-'
        
    def run(self, optlist, args):

        for o, i in optlist:
            if o in ('-h', '--help'):
                sys.stderr.write(usageString + '\n')
                sys.stderr.write(helpString + '\n')
                sys.exit(1)

            elif o in ('-v', '--version'):
                sys.stdout.write('%s\n' % str(self.version))
                sys.exit(0)

            elif o in ('-o', '--output'):
                self.options['output'] = i
                
        if len(args) < 1:
            sys.stderr.write(usageString + '\n')
            sys.exit(1)


        with open(args[0], 'r') as infile:
            rendered = mistletoe.markdown(infile, JIRARenderer)

        if self.options['output'] == '-':
            sys.stdout.write(rendered)
        else:
            with open(self.options['output'], 'w') as outfile:
                outfile.write(rendered)
        
         
if __name__ == '__main__':
    CommandLineParser()
    
    
