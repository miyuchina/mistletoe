from mistletoe.contrib.telegraph import TelegraphRenderer, md_to_telegraph
from test.base_test import BaseRendererTest


def text_content(nodes):
    parts = []
    for node in nodes:
        if isinstance(node, str):
            parts.append(node)
        elif isinstance(node, dict):
            parts.extend(text_content(node.get("children") or []))
    return "".join(parts)


class TestTelegraphRenderer(BaseRendererTest):
    def setUp(self):
        super().setUp()
        self.renderer = TelegraphRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_md_to_telegraph_function(self):
        result = md_to_telegraph("# Title")
        self.assertEqual(result, [{"tag": "h3", "children": ["Title"]}])

    def test_soft_break_space_preserved_after_link(self):
        markdown = "This is [some link](http://example.com)\nand more text."
        result = md_to_telegraph(markdown)
        self.assertEqual(len(result), 1)
        children = result[0]["children"]
        self.assertIn(" ", children)
        self.assertIn("and more text.", children)
        self.assertEqual(text_content(result), "This is some link and more text.")

    def test_soft_break_inline_code_spacing(self):
        markdown = "hiding\n`SSH`\nin HTTPS"
        result = md_to_telegraph(markdown)
        self.assertEqual(text_content(result), "hiding SSH in HTTPS")
        self.assertIn(" ", result[0]["children"])

    def test_hard_break_produces_br(self):
        result = md_to_telegraph("Line one  \nLine two")
        self.assertIn({"tag": "br"}, result[0]["children"])

    def test_heading_mapping(self):
        self.assertEqual(
            md_to_telegraph("# Title"), [{"tag": "h3", "children": ["Title"]}]
        )
        self.assertEqual(
            md_to_telegraph("## Subtitle"), [{"tag": "h4", "children": ["Subtitle"]}]
        )
        self.assertEqual(
            md_to_telegraph("### Section"),
            [{"tag": "p", "children": [{"tag": "strong", "children": ["Section"]}]}],
        )

    def test_inline_formatting(self):
        result = md_to_telegraph("This is **bold** and *italic* and `code`.")
        self.assertEqual(text_content(result), "This is bold and italic and code.")
        self.assertEqual(
            result[0]["children"][1], {"tag": "strong", "children": ["bold"]}
        )
        self.assertEqual(
            result[0]["children"][3], {"tag": "em", "children": ["italic"]}
        )
        self.assertEqual(
            result[0]["children"][5], {"tag": "code", "children": ["code"]}
        )

    def test_link_and_autolink(self):
        result = md_to_telegraph(
            '[text](http://example.com "My title") <https://example.com>'
        )
        self.assertEqual(
            result[0]["children"][0],
            {
                "tag": "a",
                "attrs": {"href": "http://example.com", "title": "My title"},
                "children": ["text"],
            },
        )
        self.assertEqual(
            result[0]["children"][2],
            {
                "tag": "a",
                "attrs": {"href": "https://example.com"},
                "children": ["https://example.com"],
            },
        )

    def test_blockquote_and_thematic_break(self):
        self.assertEqual(
            md_to_telegraph("> A quote"),
            [
                {
                    "tag": "blockquote",
                    "children": [{"tag": "p", "children": ["A quote"]}],
                }
            ],
        )
        self.assertEqual(md_to_telegraph("---"), [{"tag": "hr"}])

    def test_lists(self):
        unordered = md_to_telegraph("- item one\n- item two")
        self.assertEqual(unordered[0]["tag"], "ul")
        self.assertEqual(len(unordered[0]["children"]), 2)
        ordered = md_to_telegraph("1. first\n2. second")
        self.assertEqual(ordered[0]["tag"], "ol")

    def test_nested_list(self):
        result = md_to_telegraph("- outer\n    - inner")
        outer_item = result[0]["children"][0]
        nested_tags = [
            child["tag"] for child in outer_item["children"] if isinstance(child, dict)
        ]
        self.assertIn("ul", nested_tags)

    def test_block_code(self):
        result = md_to_telegraph("```python\nprint('hi')\n```")
        self.assertEqual(
            result,
            [
                {
                    "tag": "pre",
                    "children": [
                        {
                            "tag": "code",
                            "attrs": {"class": "language-python"},
                            "children": ["print('hi')"],
                        }
                    ],
                }
            ],
        )

    def test_block_code_multiline_has_br_nodes(self):
        result = md_to_telegraph("```\nline1\nline2\nline3\n```")
        code_children = result[0]["children"][0]["children"]
        self.assertEqual(code_children[0], "line1")
        self.assertEqual(code_children[1], {"tag": "br"})
        self.assertEqual(code_children[2], "line2")

    def test_html_passthrough(self):
        block = md_to_telegraph("<pre>\ncode here\n</pre>")
        self.assertEqual(len(block), 1)
        self.assertTrue(isinstance(block[0], str))
        self.assertIn("code here", block[0])

        span = md_to_telegraph("text <em>emphasis</em> end")
        self.assertEqual(text_content(span), "text <em>emphasis</em> end")
        self.assertTrue(
            any(
                isinstance(child, str) and "<em>" in child
                for child in span[0]["children"]
            )
        )

    def test_image_with_title(self):
        result = md_to_telegraph('![alt](http://example.com/img.png "Caption")')
        self.assertEqual(
            result[0]["children"][0],
            {
                "tag": "img",
                "attrs": {
                    "src": "http://example.com/img.png",
                    "alt": ["alt"],
                    "title": "Caption",
                },
            },
        )

    def test_whitespace_only_document_is_skipped(self):
        self.assertEqual(md_to_telegraph(""), [])
        self.assertEqual(md_to_telegraph("   \n  \n  "), [])
        self.assertEqual(md_to_telegraph("&nbsp;"), [])

    def test_nbsp_only_paragraph_in_blockquote_is_skipped(self):
        self.assertEqual(
            md_to_telegraph("> &nbsp;"),
            [{"tag": "blockquote", "children": []}],
        )
