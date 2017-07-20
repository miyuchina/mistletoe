import json

def get_ast(token):
    node = {}
    node['type'] = type(token).__name__
    node.update({key: token.__dict__[key] for key in token.__dict__})
    if 'children' in node:
        node['children'] = [get_ast(child) for child in node['children']]
    return node

def render(token):
    print(json.dumps(get_ast(token), indent=2))
