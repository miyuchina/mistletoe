import json

from mistletoe.base_renderer import BaseRenderer

ADF_VERSION = 1

class ADFRenderer(BaseRenderer):
    adf_name = {
        "Document": "doc",
        "Paragraph": "paragraph",
    }

    def render(self, token):
        """
        Returns the string representation of the ADF.

        Overrides super().render. Delegates the logic to get_adf.
        """
        return json.dumps(get_adf(token), indent=2) + '\n'

    def __getattr__(self, name):         
        return lambda token: ''

def get_adf(token):
    node = {}

    node['type'] = ADFRenderer.adf_name.get(token.__class__.__name__, token.__class__.__name__)
    node['version'] = ADF_VERSION
    node['']

    for attrname in ['content', 'footnotes']:
        if attrname in vars(token):
            node[attrname] = getattr(token, attrname)
    for attrname in token.repr_attributes:
        node[attrname] = getattr(token, attrname)
    if 'header' in vars(token):
        node['header'] = get_adf(getattr(token, 'header'))
    if token.children is not None:
        node['children'] = [get_adf(child) for child in token.children]
    return node