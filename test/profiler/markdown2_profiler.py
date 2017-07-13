import markdown2

def run():
    with open('jquery.md', 'r') as fin:
        markdown2.markdown(''.join(fin.readlines()))

if __name__ == '__main__':
    for i in range(100): run()
