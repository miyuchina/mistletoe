__all__ = ['render']

def render(node):
    token_type = type(node).__name__
    return render_map[token_type](node)

def render_bold(node):
    return tagify('b', render_inner(node))

def render_italic(node):
    return tagify('em', render_inner(node))

def render_inline_code(node):
    return tagify('code', render_inner(node))

def render_strikethrough(node):
    return tagify('del', render_inner(node))

def render_link(node):
    attrs = { 'href': node.target }
    return tagify_attrs('a', attrs, node.name)

def render_raw_text(node):
    return node.content

def render_heading(node):
    tag = 'h' + str(node.level)
    return tagify(tag, render_inner(node))

def render_quote(node):
    return tagify('blockquote', render_inner(node))

def render_paragraph(node):
    return tagify('p', render_inner(node))

def render_block_code(node):
    if node.language:
        attrs = { 'class': node.language }
        return tagify('pre', tagify_attrs('code', attrs, node.content))
    else:
        return tagify('pre', tagify('code', node.content))

def render_list_item(node):
    return tagify('li', render_inner(node))

def render_list(node):
    return tagify('ul', render_inner(node))

def render_separator(node):
    return '<hr>'

def render_document(node):
    return tagify('html', tagify('body', render_inner(node)))

def render_inner(node):
    return ''.join([ render(child) for child in node.children ])

render_map = {
    'Bold': render_bold,
    'Italic': render_italic,
    'InlineCode': render_inline_code,
    'Strikethrough': render_strikethrough,
    'Link': render_link,
    'RawText': render_raw_text,
    'Heading': render_heading,
    'Quote': render_quote,
    'Paragraph': render_paragraph,
    'BlockCode': render_block_code,
    'ListItem': render_list_item,
    'List': render_list,
    'Separator': render_separator,
    'Document': render_document
}

def tagify(tag, content):
    return "<{0}>{1}</{0}>".format(tag, content)

def tagify_attrs(tag, attrs, content):
    attrs = [ "{}=\"{}\"".format(key, attrs[key]) for key in attrs ]
    attrs = ' '.join(attrs)
    return "<{0} {1}>{2}</{0}>".format(tag, attrs, content)
