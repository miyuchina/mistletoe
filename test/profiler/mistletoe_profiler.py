import mistletoe
from mistletoe.html_token import Context
from mistletoe.html_renderer import render
from mistletoe import Document
from time import time

def run():
    with open('test/profiler/syntax.md', 'r') as fin:
        with Context():
            rendered = render(Document(fin))
        return rendered

if __name__ == '__main__':
    start = time()
    for i in range(1000): run()
    end = time()
    print(end - start)
