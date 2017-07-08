import sys
import parser

def render_file(filename):
    with open(filename, 'r') as fin:
        lines = fin.readlines()
        rendered_l = [ token.render() for token in parser.tokenize(lines) ]
        rendered = ''.join(rendered_l)
        rendered += '\n'
    return(rendered)

if __name__ == "__main__":
    try:
        print(render_file(sys.argv[1]))
    except IndexError:
        sys.exit('Not enough arguments.')
