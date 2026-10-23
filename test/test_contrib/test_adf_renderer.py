from mistletoe import token
from mistletoe.block_token import Document
from mistletoe.contrib import adf_renderer
from test.base_test import BaseRendererTest

filesBasedTest = BaseRendererTest.filesBasedTest


class TestAdfRenderer(BaseRendererTest):
    def setUp(self):
        super().setUp()
        token._root_node = Document([])
        self.renderer = adf_renderer.AdfRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)
        self.sampleOutputExtension = "adf.json"

    def test_heading(self):
        doc = Document(
            [
                "# Heading 1\n",
                "## Heading 2\n",
                "### Heading 3\n",
                "#### Heading 4\n",
                "##### Heading 5\n",
                "###### Heading 6\n",
                "Alternative Heading 1\n",
                "=====================\n",
                "Alternative Heading 2\n",
                "---------------------",
            ]
        )

        adf = adf_renderer.get_adf(doc)

        expected = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Heading 1"}],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Heading 2"}],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Heading 3"}],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 4},
                    "content": [{"type": "text", "text": "Heading 4"}],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 5},
                    "content": [{"type": "text", "text": "Heading 5"}],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 6},
                    "content": [{"type": "text", "text": "Heading 6"}],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Alternative Heading 1"}],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Alternative Heading 2"}],
                },
            ],
        }

        self.assertDictEqual(expected, adf)

    def test_table(self):
        doc = Document(
            [
                "| Left aligned | Center aligned | Right aligned |\n",
                "|:-------------|:--------------:|--------------:|\n",
                "| Text         | Text           | Text          |\n",
                "| More text    | More text      | More text     |",
            ]
        )

        expected = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "table",
                    "content": [
                        {
                            "type": "tableRow",
                            "content": [
                                {
                                    "type": "tableHeader",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "Left aligned"}
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "type": "tableHeader",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Center aligned",
                                                }
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "type": "tableHeader",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Right aligned",
                                                }
                                            ],
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "tableRow",
                            "content": [
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "Text"}
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "Text"}
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "Text"}
                                            ],
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "tableRow",
                            "content": [
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "More text"}
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "More text"}
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "type": "tableCell",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {"type": "text", "text": "More text"}
                                            ],
                                        }
                                    ],
                                },
                            ],
                        },
                    ],
                }
            ],
        }

        adf = adf_renderer.get_adf(doc)
        self.assertDictEqual(adf, expected)

    def test_marks(self):
        doc = Document(["[Test link](https://localhost)\n", "**bold**"])

        expected = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Test link",
                            "marks": [
                                {
                                    "type": "link",
                                    "attrs": {"href": "https://localhost", "title": ""},
                                }
                            ],
                        },
                        {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
                    ],
                }
            ],
        }

        adf = adf_renderer.get_adf(doc)
        self.assertDictEqual(adf, expected)

    def test_rule(self):
        doc = Document(["---"])

        expected = {"type": "doc", "version": 1, "content": [{"type": "rule"}]}
        adf = adf_renderer.get_adf(doc)
        self.assertDictEqual(adf, expected)

    @filesBasedTest
    def test_render__basic_blocks(self):
        pass

    @filesBasedTest
    def test_render__lists(self):
        pass

    @filesBasedTest
    def test_render__quotes(self):
        pass
