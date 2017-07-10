import sys
import core.block_token as block_token
import lib.html_renderer as renderer

def main(filename=""):
    fin = open(filename, 'r') if filename else sys.stdin
    lines = fin.readlines()
    markdown = block_token.Document(lines)
    fin.close()
    return renderer.render(markdown)

if __name__ == "__main__":
    try:
        print(main(sys.argv[1]))
    except IndexError:
        try:
            print(main())
        except KeyboardInterrupt:
            sys.exit('Aborted by user.')
