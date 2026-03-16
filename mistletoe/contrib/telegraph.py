"""
Render mistletoe tokens into Telegraph DOM nodes.

Telegraph pages are created by sending a list of node dictionaries to the
Telegraph API. This renderer converts Markdown into that node structure using
mistletoe's parsing pipeline, so code that already relies on mistletoe can
publish to Telegraph without adding a second Markdown implementation.

The output format follows Telegraph's Node schema documented at
https://telegra.ph/api#Node and is suitable for the ``content`` field used by
``createPage`` and related API methods. Supported Markdown features include
paragraphs, links, emphasis, strong text, inline code, images, blockquotes,
lists, code fences, thematic breaks, and raw HTML passthrough.

Heading levels are mapped to Telegraph's limited typography model: ``#`` maps
to ``h3``, ``##`` maps to ``h4``, and deeper headings are rendered as
paragraphs containing ``strong`` nodes. Soft line breaks become spaces so words
do not collapse when Markdown producers emit embedded newlines around inline
elements.

Example:

    >>> from mistletoe.contrib.telegraph import md_to_telegraph
    >>> nodes = md_to_telegraph('# Hello\\n\\nThis is **bold** text.')
    >>> payload = {'title': 'Hello', 'content': nodes}
    >>> # POST payload to https://api.telegra.ph/createPage with your
    >>> # access token, author metadata, and other Telegraph parameters.
"""

from typing import Any, Dict, List, Union

from mistletoe import Document, block_token, span_token
from mistletoe.base_renderer import BaseRenderer

__all__ = ["TelegraphRenderer", "md_to_telegraph"]


Node = Union[Dict[str, Any], str]
NodeList = List[Node]

HEADING_LEVEL_PRIMARY = 1
HEADING_LEVEL_SECONDARY = 2
_NBSP_EQUIVALENTS = ("", "&nbsp;", "&#160;", "\xa0")


class TelegraphRenderer(BaseRenderer):
    """
    Convert a mistletoe AST into Telegraph-compatible DOM nodes.
    """

    def __init__(self):
        super().__init__(span_token.HTMLSpan, block_token.HTMLBlock)

    def render_document(self, token):
        nodes = []
        for child in token.children:
            rendered = self.render(child)
            if rendered is None:
                continue
            nodes.append(rendered)
        return nodes

    def render_paragraph(self, token):
        children = self.render_inner(token)
        if self._is_blank_node_list(children):
            return None
        return {"tag": "p", "children": children}

    def render_heading(self, token):
        children = self.render_inner(token)
        if token.level == HEADING_LEVEL_PRIMARY:
            return {"tag": "h3", "children": children}
        if token.level == HEADING_LEVEL_SECONDARY:
            return {"tag": "h4", "children": children}
        return {
            "tag": "p",
            "children": [{"tag": "strong", "children": children}],
        }

    def render_list(self, token):
        tag = "ol" if token.start is not None else "ul"
        return {
            "tag": tag,
            "children": [self.render(child) for child in token.children],
        }

    def render_list_item(self, token):
        return {"tag": "li", "children": self.render_inner(token)}

    def render_strong(self, token):
        return {"tag": "strong", "children": self.render_inner(token)}

    def render_emphasis(self, token):
        return {"tag": "em", "children": self.render_inner(token)}

    def render_inline_code(self, token):
        return {"tag": "code", "children": [token.children[0].content]}

    def render_strikethrough(self, token):
        return {"tag": "del", "children": self.render_inner(token)}

    def render_image(self, token):
        attrs = {"src": token.src}
        alt_text = self.render_inner(token)
        if alt_text:
            attrs["alt"] = alt_text
        if token.title:
            attrs["title"] = token.title
        return {"tag": "img", "attrs": attrs}

    def render_link(self, token):
        attrs = {"href": token.target}
        if token.title:
            attrs["title"] = token.title
        return {"tag": "a", "attrs": attrs, "children": self.render_inner(token)}

    def render_auto_link(self, token):
        return {"tag": "a", "attrs": {"href": token.target}, "children": [token.target]}

    def render_raw_text(self, token):
        return token.content

    def render_line_break(self, token):
        if token.soft:
            return " "
        return {"tag": "br"}

    def render_block_code(self, token):
        code_dict = {
            "tag": "code",
            "children": self.code_children_from_text(token.content),
        }
        if getattr(token, "language", None):
            code_dict["attrs"] = {"class": "language-" + token.language}
        return {"tag": "pre", "children": [code_dict]}

    def render_quote(self, token):
        return {"tag": "blockquote", "children": self.render_inner(token)}

    def render_thematic_break(self, token):
        return {"tag": "hr"}

    def render_html_block(self, token):
        return token.content

    def render_html_span(self, token):
        return token.content

    def render_inner(self, token):
        result = []
        for child in token.children:
            rendered = self.render(child)
            if rendered is None or rendered == "":
                continue
            result.append(rendered)
        return result

    @staticmethod
    def code_children_from_text(text):
        lines = text.rstrip("\n").split("\n")
        children = []
        for idx, line in enumerate(lines):
            children.append(line)
            if idx != len(lines) - 1:
                children.append({"tag": "br"})
        return children

    @classmethod
    def _is_blank_node_list(cls, children):
        if not children:
            return True
        for child in children:
            if isinstance(child, dict):
                return False
            if not cls._is_blank_text(child):
                return False
        return True

    @staticmethod
    def _is_blank_text(text):
        if text in _NBSP_EQUIVALENTS:
            return True
        normalized = (
            text.replace("&nbsp;", "").replace("&#160;", "").replace("\xa0", "")
        )
        return normalized.strip() == ""


def md_to_telegraph(markdown_text):
    with TelegraphRenderer() as renderer:
        return renderer.render(Document(markdown_text))
