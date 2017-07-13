import sys
import os
sys.path.insert(0, os.getcwd())

import core.block_token as token
import lib.html_renderer as renderer

def run():
    with open('test/profiler/jquery.md', 'r') as fin:
        t = token.Document(fin)
        renderer.render(t)

if __name__ == '__main__':
    for i in range(1000): run()
