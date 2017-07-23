import sys
import mistletoe

def convert(filename):
    with open(filename, 'r') as fin:
        rendered = mistletoe.markdown(iter(fin))
    print(rendered, end='')

def interactive():
    print('mistletoe [version 0.1 alpha] (interactive)')
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
            print('\n' + mistletoe.markdown(contents), end='')
        except KeyboardInterrupt:
            print('\nExiting.')
            return

def main():
    if len(sys.argv) > 1:
        convert(sys.argv[1])
    else:
        interactive()

if __name__ == "__main__":
    main()
