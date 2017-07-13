import mistune

def run():
    with open('jquery.md', 'r') as fin:
        mistune.markdown(''.join(fin.readlines()))

if __name__ == '__main__':
    for i in range(1000): run()
