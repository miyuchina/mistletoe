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

    def test_soft_break_space_preserved_before_link(self):
        result = md_to_telegraph("Read more\n[here](http://example.com) for details.")
        self.assertEqual(text_content(result), "Read more here for details.")

    def test_soft_break_space_preserved_after_bold(self):
        result = md_to_telegraph("Hello **world**\nfoo bar.")
        self.assertEqual(text_content(result), "Hello world foo bar.")
        self.assertIn(" ", result[0]["children"])

    def test_soft_break_space_preserved_after_emphasis(self):
        result = md_to_telegraph("An *important*\nconcept.")
        self.assertEqual(text_content(result), "An important concept.")

    def test_soft_break_space_preserved_after_inline_code(self):
        result = md_to_telegraph("Run `git status`\nto check.")
        self.assertEqual(text_content(result), "Run git status to check.")

    def test_soft_break_space_preserved_between_link_and_code(self):
        result = md_to_telegraph(
            "See [docs](http://example.com)\n`ssh -L`\nfor details."
        )
        self.assertEqual(text_content(result), "See docs ssh -L for details.")

    def test_soft_break_inline_code_at_start_of_line(self):
        result = md_to_telegraph("`SSH`\ntraffic hiding")
        self.assertEqual(text_content(result), "SSH traffic hiding")
        self.assertIn(" ", result[0]["children"])

    def test_soft_break_no_duplicate_spaces(self):
        result = md_to_telegraph("Hello **world** foo bar.")
        full = text_content(result)
        self.assertNotIn("  ", full)
        self.assertEqual(full, "Hello world foo bar.")

    def test_hard_break_produces_br(self):
        result = md_to_telegraph("Line one  \nLine two")
        self.assertIn({"tag": "br"}, result[0]["children"])

    def test_heading_h1_maps_to_h3(self):
        self.assertEqual(
            md_to_telegraph("# Title"), [{"tag": "h3", "children": ["Title"]}]
        )

    def test_heading_h2_maps_to_h4(self):
        self.assertEqual(
            md_to_telegraph("## Subtitle"), [{"tag": "h4", "children": ["Subtitle"]}]
        )

    def test_heading_h3_maps_to_strong_paragraph(self):
        self.assertEqual(
            md_to_telegraph("### Section"),
            [{"tag": "p", "children": [{"tag": "strong", "children": ["Section"]}]}],
        )

    def test_heading_h4_and_deeper_map_to_strong_paragraph(self):
        for prefix in ("#### ", "##### ", "###### "):
            self.assertEqual(
                md_to_telegraph("%sDeep heading" % prefix),
                [
                    {
                        "tag": "p",
                        "children": [{"tag": "strong", "children": ["Deep heading"]}],
                    }
                ],
            )

    def test_inline_bold_text(self):
        result = md_to_telegraph("This is **bold** text.")
        self.assertEqual(text_content(result), "This is bold text.")
        self.assertEqual(
            result[0]["children"][1], {"tag": "strong", "children": ["bold"]}
        )

    def test_inline_italic_text(self):
        result = md_to_telegraph("This is *italic* text.")
        self.assertEqual(text_content(result), "This is italic text.")
        self.assertEqual(
            result[0]["children"][1], {"tag": "em", "children": ["italic"]}
        )

    def test_inline_code(self):
        result = md_to_telegraph("Use `print()` to output.")
        self.assertEqual(text_content(result), "Use print() to output.")
        self.assertEqual(
            result[0]["children"][1], {"tag": "code", "children": ["print()"]}
        )

    def test_inline_link_with_title(self):
        result = md_to_telegraph('[text](http://example.com "My title")')
        self.assertEqual(
            result[0]["children"][0],
            {
                "tag": "a",
                "attrs": {"href": "http://example.com", "title": "My title"},
                "children": ["text"],
            },
        )

    def test_inline_autolink(self):
        result = md_to_telegraph("<https://example.com>")
        self.assertEqual(
            result[0]["children"][0],
            {
                "tag": "a",
                "attrs": {"href": "https://example.com"},
                "children": ["https://example.com"],
            },
        )

    def test_inline_bold_inside_link(self):
        result = md_to_telegraph("[**bold**](http://example.com)")
        self.assertEqual(
            result[0]["children"][0],
            {
                "tag": "a",
                "attrs": {"href": "http://example.com"},
                "children": [{"tag": "strong", "children": ["bold"]}],
            },
        )

    def test_inline_code_inside_link(self):
        result = md_to_telegraph("[`code`](http://example.com)")
        self.assertEqual(
            result[0]["children"][0],
            {
                "tag": "a",
                "attrs": {"href": "http://example.com"},
                "children": [{"tag": "code", "children": ["code"]}],
            },
        )

    def test_link_followed_by_autolink(self):
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

    def test_blockquote(self):
        self.assertEqual(
            md_to_telegraph("> A quote"),
            [
                {
                    "tag": "blockquote",
                    "children": [{"tag": "p", "children": ["A quote"]}],
                }
            ],
        )

    def test_blockquote_with_link(self):
        result = md_to_telegraph("> A [linked](http://example.com) quote")
        self.assertEqual(result[0]["tag"], "blockquote")
        self.assertEqual(text_content(result), "A linked quote")

    def test_thematic_break(self):
        self.assertEqual(md_to_telegraph("---"), [{"tag": "hr"}])

    def test_unordered_list(self):
        unordered = md_to_telegraph("- item one\n- item two")
        self.assertEqual(unordered[0]["tag"], "ul")
        self.assertEqual(len(unordered[0]["children"]), 2)

    def test_ordered_list(self):
        ordered = md_to_telegraph("1. first\n2. second")
        self.assertEqual(ordered[0]["tag"], "ol")

    def test_nested_list(self):
        result = md_to_telegraph("- outer\n    - inner")
        outer_item = result[0]["children"][0]
        nested_tags = [
            child["tag"] for child in outer_item["children"] if isinstance(child, dict)
        ]
        self.assertIn("ul", nested_tags)

    def test_list_item_with_inline_elements(self):
        result = md_to_telegraph("- item with **bold** text")
        self.assertEqual(text_content(result), "item with bold text")

    def test_block_code_with_language(self):
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

    def test_block_code_without_language(self):
        result = md_to_telegraph("```\nplain code\n```")
        code_node = result[0]["children"][0]
        self.assertEqual(code_node["tag"], "code")
        self.assertFalse("attrs" in code_node)

    def test_block_code_multiline_has_br_nodes(self):
        result = md_to_telegraph("```\nline1\nline2\nline3\n```")
        code_children = result[0]["children"][0]["children"]
        self.assertEqual(code_children[0], "line1")
        self.assertEqual(code_children[1], {"tag": "br"})
        self.assertEqual(code_children[2], "line2")

    def test_multiple_paragraphs(self):
        result = md_to_telegraph("First paragraph.\n\nSecond paragraph.")
        self.assertEqual(
            result,
            [
                {"tag": "p", "children": ["First paragraph."]},
                {"tag": "p", "children": ["Second paragraph."]},
            ],
        )

    def test_html_block_passthrough(self):
        block = md_to_telegraph("<pre>\ncode here\n</pre>")
        self.assertEqual(len(block), 1)
        self.assertTrue(isinstance(block[0], str))
        self.assertIn("code here", block[0])

    def test_html_span_passthrough(self):
        span = md_to_telegraph("text <em>emphasis</em> end")
        self.assertEqual(text_content(span), "text <em>emphasis</em> end")
        self.assertTrue(
            any(
                isinstance(child, str) and "<em>" in child
                for child in span[0]["children"]
            )
        )

    def test_image_tag(self):
        result = md_to_telegraph("![alt text](http://example.com/img.png)")
        self.assertEqual(
            result[0]["children"][0],
            {
                "tag": "img",
                "attrs": {
                    "src": "http://example.com/img.png",
                    "alt": ["alt text"],
                },
            },
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

    def test_image_no_alt_text(self):
        result = md_to_telegraph("![](http://example.com/img.png)")
        self.assertEqual(
            result[0]["children"][0],
            {
                "tag": "img",
                "attrs": {"src": "http://example.com/img.png"},
            },
        )

    def test_empty_document(self):
        self.assertEqual(md_to_telegraph(""), [])

    def test_whitespace_only_document(self):
        self.assertEqual(md_to_telegraph("   \n  \n  "), [])

    def test_nbsp_only_paragraph_is_skipped(self):
        self.assertEqual(md_to_telegraph("&nbsp;"), [])

    def test_nbsp_only_paragraph_in_blockquote_is_skipped(self):
        self.assertEqual(
            md_to_telegraph("> &nbsp;"),
            [{"tag": "blockquote", "children": []}],
        )
