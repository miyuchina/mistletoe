import mistletoe
import mistletoe.html_token
from mistletoe.html_renderer import render
from mistletoe import Document

def run():
    with open('test/profiler/jquery.md', 'r') as fin:
        rendered = render(Document(fin))
        return rendered

if __name__ == '__main__':
    for i in range(1000): run()
