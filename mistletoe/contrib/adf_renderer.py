import json

from mistletoe.base_renderer import BaseRenderer
from mistletoe.span_token import Emphasis, LineBreak, Strikethrough, Strong


class ADFRenderer(BaseRenderer):

    ADF_VERSION = 1
    current_marks = []

    def __init__(self):
        self.adf_func = {
            "Document": self.adf_doc_node,
            "RawText": self.adf_text_node,
            "Heading": self.adf_heading_node,
            "Paragraph": self.adf_paragraph_node,
            "Emphasis": self.adf_marks
        }

    def adf_doc_node(self, token):
        return {
            "type": "doc",
            "version": self.ADF_VERSION,
            "content": self.get_child_nodes(token),
        }

    def adf_marks(self, token):
        self.current_marks.append({"type": self.discover_mark_type(token)})
        return self.get_child_nodes(token)

    def adf_heading_node(self, token):
        return {
            "type": "heading",
            "attrs": {"level": getattr(token, "level")},
            "content": self.get_child_nodes(token),
        }

    def adf_paragraph_node(self, token):
        return {"type": "paragraph", "content": self.get_child_nodes(token)}

    def get_child_nodes(self, token):
        return [
            self.adf_func[child.__class__.__name__](child)
            for child in getattr(token, "children")
            if not isinstance(child, (LineBreak, Emphasis))
        ]

    def adf_text_node(self, token):
        node = {}
        node["type"] = "text"
        node["text"] = getattr(token, "content").replace("\n", " ")
        node.update(self.adf_span_node_preprocess())

        return node

    def adf_span_node_preprocess(self):
        node = {}
        node["marks"] = [mark for mark in self.current_marks]
        self.current_marks = []
        return node

    def discover_mark_type(self, token):
        if isinstance(token, Emphasis):
            return "em"
        if isinstance(token, Strong):
            return "strong"
        if isinstance(token, Strikethrough):
            return "strike"

    def render(self, token):
        """
        Returns the string representation of the ADF.

        Overrides super().render. Delegates the logic to get_adf.
        """

        return json.dumps(get_adf(token, ADFRenderer()), indent=2) + "\n"

    def __getattr__(self, name):
        return lambda token: ""



def get_adf(token, renderer):
    node = renderer.adf_func[token.__class__.__name__](token)
    return node
