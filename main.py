import sys
import core.block_token as block_token
import lib.html_renderer as renderer

def main(filename=None):
    fin = open(filename, 'r') if filename else sys.stdin
    markdown = block_token.Document(iter(fin))
    rendered = renderer.HTMLRenderer().render(markdown)
    fin.close()
    return rendered

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(main(sys.argv[1]))
    else:
        try:
            print(main())
        except KeyboardInterrupt:
            sys.exit('Aborted by user.')
