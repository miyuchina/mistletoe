import mistune
from time import time

def run():
    with open('test/profiler/syntax.md', 'r') as fin:
        mistune.markdown(fin.read())

if __name__ == '__main__':
    start = time()
    for i in range(1000): run()
    end = time()
    print(end - start)
