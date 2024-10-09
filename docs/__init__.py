from mistletoe import Document, HtmlRenderer, __version__

INCLUDE = {'README.md': 'index.html',
           'CONTRIBUTING.md': 'contributing.html'}

METADATA = """
<head>
  <title>mistletoe{}</title>
  <meta charset="UTF-8" />
  <meta name="description" content="A fast, extensible Markdown parser in Python." />
  <meta name="keywords" content="Markdown,Python,LaTeX,HTML" />
  <meta name="author" content="Mi Yu" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="style.css" type="text/css" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/styles/github.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/highlight.min.js"></script>
  <script>hljs.initHighlightingOnLoad();</script>
</head>
"""


class DocRenderer(HtmlRenderer):
    def render_link(self, token):
        return super().render_link(self._replace_link(token))

    def render_document(self, token, name="README.md"):
        pattern = "<html>{}<body>{}</body></html>"
        self.footnotes.update(token.footnotes)
        for filename, new_link in getattr(self, 'files', {}).items():
            for k, v in self.footnotes.items():
                if v == filename:
                    self.footnotes[k] = new_link
        subtitle = ' | {}'.format('version ' + __version__ if name == 'README.md' else name.split('.')[0].lower())
        return pattern.format(METADATA.format(subtitle), self.render_inner(token))

    def _replace_link(self, token):
        token.target = getattr(self, 'files', {}).get(token.target, token.target)
        return token


def build(files=None):
    files = files or INCLUDE
    for f in files:
        with open(f, 'r', encoding='utf-8') as fin:
            rendered_file = 'docs/' + files[f]
            with open(rendered_file, 'w+', encoding='utf-8') as fout:
                with DocRenderer() as renderer:
                    renderer.files = files
                    print(renderer.render_document(Document(fin), f), file=fout)
