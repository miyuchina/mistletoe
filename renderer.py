import parser

def render_file(filename):
    with open(filename, 'r') as fin:
        lines = fin.readlines()
        rendered_l = [ token.render() for token in parser.tokenize(lines) ]
        rendered = ''.join(rendered_l)
    print(rendered)

if __name__ == "__main__":
    render_file('test.md')
