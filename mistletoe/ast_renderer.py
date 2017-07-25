"""
Abstract syntax tree renderer for mistletoe.
"""

import json

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
    if 'children' in node:
        node['children'] = [get_ast(child) for child in node['children']]
    return node

def render(token):
    """
    Returns the string representation of the AST; compliant with other
    renderer.render functions.
    """
    return json.dumps(get_ast(token), indent=2)
