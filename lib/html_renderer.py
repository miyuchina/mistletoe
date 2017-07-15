import html

__all__ = ['render']

def render(node):
    token_type = type(node).__name__
    return render_map[token_type](node)

def render_strong(node):
    return tagify('strong', render_inner(node))

def render_emphasis(node):
    return tagify('em', render_inner(node))

def render_inline_code(node):
    return tagify('code', render_inner(node))

def render_strikethrough(node):
    return tagify('del', render_inner(node))

def render_image(node):
    return '<img src="{}" alt="{}" title="{}">'.format(node.target,
                                                       node.alt,
                                                       node.title)

def render_link(node):
    attrs = { 'href': node.target }
    return tagify_attrs('a', attrs, node.name)

def render_raw_text(node):
    return html.escape(node.content)

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
    if hasattr(node, 'start'):
        attrs = { 'start': node.start }
        return tagify_attrs('ol', attrs, render_inner(node))
    else:
        return tagify('ul', render_inner(node))

def render_separator(node):
    return '<hr>'

def render_document(node):
    return tagify('html', tagify('body', render_inner(node)))

def render_inner(node):
    return ''.join([ render(child) for child in node.children ])

render_map = {
    'Strong': render_strong,
    'Emphasis': render_emphasis,
    'InlineCode': render_inline_code,
    'Strikethrough': render_strikethrough,
    'Image': render_image,
    'Link': render_link,
    'EscapeSequence': render_raw_text,
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
