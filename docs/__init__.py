from mistletoe import markdown, HTMLRenderer

INCLUDE = ['README.md', 'CONTRIBUTING.md',]

METADATA = """
<head>
  <title>mistletoe</title>
  <meta charset="UTF-8" />
  <meta name="description" content="A fast, extensible Markdown parser in Python." />
  <meta name="keywords" content="Markdown,Python,LaTeX,HTML" />
  <meta name="author" content="Mi Yu" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="style.css" type="text/css" />
</head>
"""

class DocRenderer(HTMLRenderer):
    def render_document(self, token):
        pattern = "<html>{}<body>{}</body></html>"
        inner = super().render_document(token)
        return pattern.format(METADATA, inner)

def build(files=None):
    files = files or INCLUDE
    for f in files:
        with open(f, 'r') as fin:
            rendered_file = 'docs/' + f.split('.')[0] + '.html'
            with open(rendered_file, 'w+') as fout:
                print(markdown(fin, DocRenderer), file=fout)

