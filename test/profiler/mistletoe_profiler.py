import mistletoe
from time import time

def run():
    with open('test/profiler/syntax.md', 'r') as fin:
        return mistletoe.markdown(fin)

if __name__ == '__main__':
    start = time()
    for i in range(1000): run()
    end = time()
    print(end - start)
