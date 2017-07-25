import markdown

def run():
    with open('jquery.md', 'r') as fin:
        markdown.markdown(fin.read())

if __name__ == '__main__':
    for i in range(1000): run()
