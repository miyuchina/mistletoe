import sys
import datetime
import core.block_token as block_token
import lib.html_renderer as renderer

def convert(filename):
    with open(filename, 'r') as fin:
        markdown = block_token.Document(iter(fin))
        rendered = renderer.HTMLRenderer().render(markdown)
    print(rendered)

def interactive():
    time = datetime.datetime.now().date()
    print('mistletoe [version 0.9.0 alpha] (interactive, {})'.format(time))
    print('Type Ctrl-D to complete input, or Ctrl-C to exit.')
    while True:
        try:
            contents = []
            print('>>> ', end='')
            while True:
                try:
                    line = input() + '\n'
                except EOFError:
                    break
                contents.append(line)
                print('... ', end='')
            markdown = block_token.Document(contents)
            rendered = renderer.HTMLRenderer().render(markdown)
            print('\n' + rendered)
        except KeyboardInterrupt:
            print('\nTerminated by user.')
            return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        convert(sys.argv[1])
    else:
        interactive()
