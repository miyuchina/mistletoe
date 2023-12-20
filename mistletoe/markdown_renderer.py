"""
Markdown renderer for mistletoe.
"""

import re
from itertools import chain
from typing import Iterable, Sequence

from mistletoe import block_token, span_token, token
from mistletoe.base_renderer import BaseRenderer


class BlankLine(block_token.BlockToken):
    """
    Blank line token. Represents a single blank line.
    This is a leaf block token without children.
    """

    pattern = re.compile(r"\s*\n$")

    def __init__(self, _):
        self.children = []

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @classmethod
    def read(cls, lines):
        return [next(lines)]


class LinkReferenceDefinition(span_token.SpanToken):
    """
    Link reference definition. ([label]: dest "title")

    Not included in the parsing process, but called by `LinkReferenceDefinitionBlock`.

    Attributes:
        label (str): link label, used in link references.
        dest (str): link target.
        title (str): link title (default to empty).
    """

    repr_attributes = ("label", "dest", "title")

    def __init__(self, match):
        self.label, self.dest, self.title, self.dest_type, self.title_delimiter = match


class LinkReferenceDefinitionBlock(block_token.Footnote):
    """
    A sequence of link reference definitions.
    This is a leaf block token. Its children are link reference definition tokens.

    This class inherits from `Footnote` and modifies the behavior of the constructor,
    to keep the tokens in the AST.
    """

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj

    def __init__(self, matches):
        self.children = [LinkReferenceDefinition(match) for match in matches]


class Fragment:
    """
    Markdown fragment. Used when rendering trees of span tokens into flat sequences.
    May carry additional data in addition to the text.

    Attributes:
        text (str): markdown fragment.
    """

    def __init__(self, text: str, **extras):
        self.text = text
        self.__dict__.update(extras)


class MarkdownRenderer(BaseRenderer):
    """
    Markdown renderer.

    Designed to make as "clean" a roundtrip as possible, markdown -> parsing -> rendering -> markdown,
    except for nonessential whitespace. Except when rendering with word wrapping enabled.

    Includes `HtmlBlock` and `HtmlSpan` tokens in the parsing.
    """

    _whitespace = re.compile(r"\s+")

    def __init__(
        self,
        *extras,
        max_line_length: int = None,
        normalize_whitespace=False
    ):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
            max_line_length (int): if specified, the document is word wrapped to the
                specified line length when rendered. Otherwise the formatting from the
                original (parsed) document is retained as much as possible.
            normalize_whitespace (bool): if `False`, the renderer will try to preserve
                as much whitespace as it currently can. For example, you can
                use this flag to control whether to replace the original
                spacing after every list item leader with just 1 space.
        """
        block_token.remove_token(block_token.Footnote)
        super().__init__(
            *chain(
                (
                    block_token.HtmlBlock,
                    span_token.HtmlSpan,
                    BlankLine,
                    LinkReferenceDefinitionBlock,
                ),
                extras,
            )
        )
        self.render_map["SetextHeading"] = self.render_setext_heading
        self.render_map["CodeFence"] = self.render_fenced_code_block
        self.render_map[
            "LinkReferenceDefinition"
        ] = self.render_link_reference_definition
        self.max_line_length = max_line_length
        self.normalize_whitespace = normalize_whitespace

    def render(self, token: token.Token) -> str:
        """
        Renders the tree of tokens rooted at the given token into markdown.
        """
        if isinstance(token, block_token.BlockToken):
            lines = self.render_map[token.__class__.__name__](
                token, max_line_length=self.max_line_length
            )
        else:
            lines = self.span_to_lines([token], max_line_length=self.max_line_length)

        return "".join(map(lambda line: line + "\n", lines))

    # rendering of span/inline tokens.
    # rendered into sequences of Fragments.

    def render_raw_text(self, token) -> Iterable[Fragment]:
        yield Fragment(token.content, wordwrap=True)

    def render_strong(self, token: span_token.Strong) -> Iterable[Fragment]:
        return self.embed_span(Fragment(token.delimiter * 2), token.children)

    def render_emphasis(self, token: span_token.Emphasis) -> Iterable[Fragment]:
        return self.embed_span(Fragment(token.delimiter), token.children)

    def render_inline_code(self, token: span_token.InlineCode) -> Iterable[Fragment]:
        return self.embed_span(
            Fragment(token.delimiter + token.padding),
            token.children,
            Fragment(token.padding + token.delimiter)
        )

    def render_strikethrough(
        self, token: span_token.Strikethrough
    ) -> Iterable[Fragment]:
        return self.embed_span(Fragment("~~"), token.children)

    def render_image(self, token: span_token.Image) -> Iterable[Fragment]:
        yield Fragment("!")
        yield from self.render_link_or_image(token, token.src)

    def render_link(self, token: span_token.Link) -> Iterable[Fragment]:
        return self.render_link_or_image(token, token.target)

    def render_link_or_image(
        self, token: span_token.SpanToken, target: str
    ) -> Iterable[Fragment]:
        yield from self.embed_span(
            Fragment("["),
            token.children,
            Fragment("]"),
        )

        if token.dest_type == "uri" or token.dest_type == "angle_uri":
            # "[" description "](" dest_part [" " title] ")"
            yield Fragment("(")
            dest_part = "<" + target + ">" if token.dest_type == "angle_uri" else target
            yield Fragment(dest_part)
            if token.title:
                yield from (
                    Fragment(" ", wordwrap=True),
                    Fragment(token.title_delimiter),
                    Fragment(token.title, wordwrap=True),
                    Fragment(
                        ")" if token.title_delimiter == "(" else token.title_delimiter,
                    ),
                )
            yield Fragment(")")
        elif token.dest_type == "full":
            # "[" description "][" label "]"
            yield from (
                Fragment("["),
                Fragment(token.label, wordwrap=True),
                Fragment("]"),
            )
        elif token.dest_type == "collapsed":
            # "[" description "][]"
            yield Fragment("[]")
        else:
            # "[" description "]"
            pass

    def render_auto_link(self, token: span_token.AutoLink) -> Iterable[Fragment]:
        yield Fragment("<" + token.children[0].content + ">")

    def render_escape_sequence(
        self, token: span_token.EscapeSequence
    ) -> Iterable[Fragment]:
        yield Fragment("\\" + token.children[0].content)

    def render_line_break(self, token: span_token.LineBreak) -> Iterable[Fragment]:
        yield Fragment(
            token.content + "\n", wordwrap=token.soft, hard_line_break=not token.soft
        )

    def render_html_span(self, token: span_token.HtmlSpan) -> Iterable[Fragment]:
        yield Fragment(token.content)

    def render_link_reference_definition(
        self, token: LinkReferenceDefinition
    ) -> Iterable[Fragment]:
        yield from (
            Fragment("["),
            Fragment(token.label, wordwrap=True),
            Fragment("]: ", wordwrap=True),
            Fragment(
                "<" + token.dest + ">"
                if token.dest_type == "angle_uri"
                else token.dest,
            ),
        )
        if token.title:
            yield from (
                Fragment(" ", wordwrap=True),
                Fragment(token.title_delimiter),
                Fragment(token.title, wordwrap=True),
                Fragment(
                    ")" if token.title_delimiter == "(" else token.title_delimiter,
                ),
            )

    # rendering of block tokens.
    # rendered into sequences of lines (strings), to be joined by newlines.

    def render_document(
        self, token: block_token.Document, max_line_length: int
    ) -> Iterable[str]:
        return self.blocks_to_lines(token.children, max_line_length=max_line_length)

    def render_heading(
        self, token: block_token.Heading, max_line_length: int
    ) -> Iterable[str]:
        # note: no word wrapping, because atx headings always fit on a single line.
        line = "#" * token.level
        text = next(self.span_to_lines(token.children, max_line_length=None), "")
        if text:
            line += " " + text
        if token.closing_sequence:
            line += " " + token.closing_sequence
        return [line]

    def render_setext_heading(
        self, token: block_token.SetextHeading, max_line_length: int
    ) -> Iterable[str]:
        yield from self.span_to_lines(token.children, max_line_length=max_line_length)
        yield token.underline

    def render_quote(
        self, token: block_token.Quote, max_line_length: int
    ) -> Iterable[str]:
        max_child_line_length = max_line_length - 2 if max_line_length else None
        lines = self.blocks_to_lines(
            token.children, max_line_length=max_child_line_length
        )
        return self.prefix_lines(lines or [""], "> ")

    def render_paragraph(
        self, token: block_token.Paragraph, max_line_length: int
    ) -> Iterable[str]:
        return self.span_to_lines(token.children, max_line_length=max_line_length)

    def render_block_code(
        self, token: block_token.BlockCode, max_line_length: int
    ) -> Iterable[str]:
        lines = token.content[:-1].split("\n")
        return self.prefix_lines(lines, "    ")

    def render_fenced_code_block(
        self, token: block_token.BlockCode, max_line_length: int
    ) -> Iterable[str]:
        indentation = " " * token.indentation
        yield indentation + token.delimiter + token.info_string
        yield from self.prefix_lines(
            token.content[:-1].split("\n"), indentation
        )
        yield indentation + token.delimiter

    def render_list(
        self, token: block_token.List, max_line_length: int
    ) -> Iterable[str]:
        return self.blocks_to_lines(token.children, max_line_length=max_line_length)

    def render_list_item(
        self, token: block_token.ListItem, max_line_length: int
    ) -> Iterable[str]:
        indentation = len(token.leader) + 1 if self.normalize_whitespace else token.prepend - token.indentation
        max_child_line_length = (
            max_line_length - indentation if max_line_length else None
        )
        lines = self.blocks_to_lines(
            token.children, max_line_length=max_child_line_length
        )
        return self.prefix_lines(
            list(lines) or [""],
            token.leader + " " * (indentation - len(token.leader)),
            " " * indentation
        )

    def render_table(
        self, token: block_token.Table, max_line_length: int
    ) -> Iterable[str]:
        # note: column widths are not preserved; they are automatically adjusted to fit the contents.
        content = [self.table_row_to_text(token.header), []]
        content.extend(self.table_row_to_text(row) for row in token.children)
        col_widths = self.calculate_table_column_widths(content)
        content[1] = self.table_separator_line_to_text(col_widths, token.column_align)
        return [
            self.table_row_to_line(col_text, col_widths, token.column_align)
            for col_text in content
        ]

    def render_thematic_break(
        self, token: block_token.ThematicBreak, max_line_length: int
    ) -> Iterable[str]:
        return [token.line]

    def render_html_block(
        self, token: block_token.HtmlBlock, max_line_length: int
    ) -> Iterable[str]:
        return token.content.split("\n")

    def render_link_reference_definition_block(
        self, token: LinkReferenceDefinitionBlock, max_line_length: int
    ) -> Iterable[str]:
        # each link reference definition starts on a new line
        for child in token.children:
            yield from self.span_to_lines([child], max_line_length=max_line_length)

    def render_blank_line(
        self, token: BlankLine, max_line_length: int
    ) -> Iterable[str]:
        return [""]

    # helper methods

    def embed_span(
        self,
        leader: Fragment,
        tokens: Iterable[span_token.SpanToken],
        trailer: Fragment = None,
    ) -> Iterable[Fragment]:
        """
        Makes fragments from `tokens` and embeds within a leader and a trailer.
        The trailer defaults to the same as the leader.
        """
        yield leader
        yield from self.make_fragments(tokens)
        yield trailer or leader

    def blocks_to_lines(
        self, tokens: Iterable[block_token.BlockToken], max_line_length: int
    ) -> Iterable[str]:
        """
        Renders a sequence of block tokens into a sequence of lines.
        """
        for token in tokens:  # noqa: F402
            yield from self.render_map[token.__class__.__name__](
                token, max_line_length=max_line_length
            )

    def span_to_lines(
        self, tokens: Iterable[span_token.SpanToken], max_line_length: int
    ) -> Iterable[str]:
        """
        Renders a sequence of span (inline) tokens into a sequence of lines.
        """
        fragments = self.make_fragments(tokens)
        return self.fragments_to_lines(fragments, max_line_length=max_line_length)

    def make_fragments(self, tokens: Iterable[span_token.SpanToken]
    ) -> Iterable[Fragment]:
        """
        Renders a sequence of span (inline) tokens into a sequence of Fragments.
        """
        return chain.from_iterable(
            [self.render_map[token.__class__.__name__](token) for token in tokens]
        )

    @classmethod
    def fragments_to_lines(
        cls, fragments: Iterable[Fragment], max_line_length: int = None
    ) -> Iterable[str]:
        """
        Renders a sequence of Fragments into lines.
        With word wrapping, if a `max_line_length` is given, or else following the
        original text flow as closely as possible.
        """
        current_line = ""
        if not max_line_length:
            # plain rendering: merge all fragments and split on newlines
            for fragment in fragments:
                if "\n" in fragment.text:
                    lines = fragment.text.split("\n")
                    yield current_line + lines[0]
                    for inner_line in lines[1:-1]:
                        yield inner_line
                    current_line = lines[-1]
                else:
                    current_line += fragment.text
        else:
            # render with word wrapping
            for word in cls.make_words(fragments):
                if word == "\n":
                    # hard line break
                    yield current_line
                    current_line = ""
                    continue

                if not current_line:
                    # first word on an empty line: accept and continue
                    current_line = word
                    continue

                # try to fit the word on the current line.
                # if it doesn't fit, flush the line and start on the next
                test = current_line + " " + word
                if len(test) <= max_line_length:
                    current_line = test
                else:
                    yield current_line
                    current_line = word

        if current_line:
            yield current_line

    @classmethod
    def make_words(cls, fragments: Iterable[Fragment]) -> Iterable[str]:
        """
        Aggregates and splits a sequence of Fragments into words, i.e., strings
        which do not contain breakable spaces or line breaks. The exception is
        hard line breaks, which are represented by the string `\n`.
        """
        word = ""
        for fragment in fragments:
            if getattr(fragment, "wordwrap", False):
                first = True
                for item in cls._whitespace.split(fragment.text):
                    if first:
                        word += item
                        first = False
                    else:
                        if word:
                            yield word
                        word = item
            elif getattr(fragment, "hard_line_break", False):
                yield from (word + fragment.text[:-1], "\n")
                word = ""
            else:
                word += fragment.text

        if word:
            yield word

    @classmethod
    def prefix_lines(
        cls,
        lines: Iterable[str],
        first_line_prefix: str,
        following_line_prefix: str = None,
    ) -> Iterable[str]:
        """
        Prepends a prefix string to a sequence of lines. The first line may
        have a different prefix from the following lines.
        """
        following_line_prefix = following_line_prefix or first_line_prefix
        is_first_line = True
        for line in lines:
            if is_first_line:
                prefixed = first_line_prefix + line
                is_first_line = False
            else:
                prefixed = following_line_prefix + line
            yield prefixed if not prefixed.isspace() else ""

    def table_row_to_text(self, row) -> Sequence[str]:
        """
        Renders each table cell on a table row to text. No word wrapping.
        """
        return [next(self.span_to_lines(col.children, max_line_length=None), "") for col in row.children]

    @classmethod
    def calculate_table_column_widths(cls, col_text) -> Sequence[int]:
        """
        Calculates column widths for a table.
        """
        MINIMUM_COLUMN_WIDTH = 3
        col_widths = []
        for row in col_text:
            while len(col_widths) < len(row):
                col_widths.append(MINIMUM_COLUMN_WIDTH)
            for index, text in enumerate(row):
                col_widths[index] = max(col_widths[index], len(text))
        return col_widths

    @classmethod
    def table_separator_line_to_text(cls, col_widths, col_align) -> Sequence[str]:
        """
        Creates the text for the line separating header from contents in a table
        given column widths and alignments.

        Note: uses dashes for left justified columns, not a colon followed by dashes.
        """
        separator_text = []
        for index, width in enumerate(col_widths):
            align = col_align[index] if index < len(col_align) else None
            sep = ":" if align == 0 else "-"
            sep += "-" * (width - 2)
            sep += ":" if align == 0 or align == 1 else "-"
            separator_text.append(sep)
        return separator_text

    @classmethod
    def table_row_to_line(cls, col_text, col_widths, col_align) -> str:
        """
        Pads/aligns the text for a table row and add the borders (pipe characters).
        """
        padded_text = []
        for index, width in enumerate(col_widths):
            text = col_text[index] if index < len(col_text) else ""
            align = col_align[index] if index < len(col_align) else None
            if align is None:
                padded_text.append("{0: <{w}}".format(text, w=width))
            elif align == 0:
                padded_text.append("{0: ^{w}}".format(text, w=width))
            else:
                padded_text.append("{0: >{w}}".format(text, w=width))
        return "".join(("| ", " | ".join(padded_text), " |"))
