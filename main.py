import sys
import parser

def main(filename=""):
    fin = open(filename, 'r') if filename else sys.stdin
    lines = fin.readlines()
    rendered_l = [ token.render() for token in parser.tokenize(lines) ]
    rendered = ''.join(rendered_l)
    rendered += '\n'
    fin.close()
    return(rendered)

if __name__ == "__main__":
    try:
        print(main(sys.argv[1]))
    except IndexError:
        try:
            print(main())
        except KeyboardInterrupt:
            sys.exit('Aborted by user.')
