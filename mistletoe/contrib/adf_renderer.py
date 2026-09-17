"""
Abstract syntax tree renderer for mistletoe.
"""

import json
from mistletoe.base_renderer import BaseRenderer


def determine_list_type(token, node):
    if token.children:
        leader: str = getattr(token.children[0], "leader").replace(".", "")
        if leader.isdecimal():
            node['attrs'] = {}
            node['attrs']['order'] = leader
            return "orderedList"
        

    return "bulletList"


ADF_TYPE = {
    "Document": "doc",
    "Heading": "heading",
    "RawText": "text",
    "Paragraph": "paragraph",
    "Emphasis": "em",
    "Strong": "strong",
    "Strikethrough": "strike",
    "LineBreak": None,
    "Link": "link",
    "InlineCode": "code",
    "CodeFence": "codeBlock",
    "List": determine_list_type,
    "ListItem": "listItem",
}

ADF_ATTRS = {
    "level": "level",
    "target": "href",
    "title": "title",
    "language": "language",
}
MARK_VALUES = ("em", "strong", "strike", "link", "code")


class AdfRenderer(BaseRenderer):
    def render(self, token):
        """
        Returns the string representation of the ADF.

        Overrides super().render. Delegates the logic to get_adf       
        """
        return json.dumps(get_adt(token), indent=2) + "\n"

    def __getattr__(self, name):
        return lambda token: ""


def get_adt(token, marks=None):
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
    #   [1]: https://docs.python.org/3/whatsNonenew/3.6.html
    #   [2]: https://github.com/syntax-tree/mdast
    node["type"] = (
       (ADF_TYPE[token.__class__.__name__])(token, node)
        if callable(ADF_TYPE[token.__class__.__name__])
        else ADF_TYPE[token.__class__.__name__]
    )

    if node["type"] is not None:
        if node["type"] == "doc":
            node["version"] = 1

        if "content" in vars(token):
            node["text"] = getattr(token, "content").replace("\n", "")
        for attrname in token.repr_attributes:
            if ADF_ATTRS.get(attrname, None) is not None:
                node["attrs"] = {} if node.get("attrs", None) is None else node["attrs"]
                node["attrs"][ADF_ATTRS[attrname]] = getattr(token, attrname)
        if node["type"] in MARK_VALUES:
            marks = [] if marks is None else marks
            if node.get("attrs", None) is not None:
                if len(node["attrs"]) == 0:
                    del node["attrs"]
            marks.append(node)
            return get_adt(token.children[0], marks)
        if "header" in vars(token):
            node["header"] = get_adt(getattr(token, "header"))
        if token.children is not None:
            node["content"] = [
                get_adt(child)
                for child in token.children
                if ADF_TYPE[child.__class__.__name__]
            ]
    else:
        if token.children is not None:
            return [
                get_adt(child)
                for child in token.children
                if ADF_TYPE[child.__class__.__name__]
            ]

    if node.get("attrs", None) is not None:
        if len(node["attrs"]) == 0:
            del node["attrs"]
    if marks is not None and len(marks) > 0:
        node["marks"] = marks
    return node
