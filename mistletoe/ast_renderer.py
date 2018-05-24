"""
Abstract syntax tree renderer for mistletoe.
"""

import json
from mistletoe.base_renderer import BaseRenderer

class ASTRenderer(BaseRenderer):
    def render(self, token):
        """
        Returns the string representation of the AST.

        Overrides super().render. Delegates the logic to get_ast.
        """
        return json.dumps(get_ast(token), indent=2) + '\n'

    def __getattr__(self, name):
        return lambda token: ''

def get_ast(token):
    """
    Recursively unrolls token attributes into dictionaries (token.children
    into lists).

    Returns:
        a dictionary of token's attributes.
    """
    node = {}
    # Python 3.6 uses [ordered dicts] [1].
    # Put in 'type' entry first to make the final tree format somewhat
    # similar to [MDAST] [2].
    #
    #   [1]: https://docs.python.org/3/whatsnew/3.6.html
    #   [2]: https://github.com/syntax-tree/mdast
    node['type'] = token.__class__.__name__
    node.update({key: token.__dict__[key] for key in token.__dict__})
    if 'target' in node and node['target'].__class__.__name__ == 'FootnoteAnchor':
        node['target'] = {'type': 'FootnoteAnchor', 'key': node['target'].key}
    if 'children' in node:
        node['children'] = [get_ast(child) for child in node['children']]
    return node
