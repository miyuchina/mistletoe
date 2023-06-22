# Test document for line numbers

See test_line_numbers.py.
Every number written as inline code should match the line number of its nearest
parent block token. Same with titles of link reference definitions.

## Heading `7`

Basic paragraph.

> Block quote (with a paragraph inside)
> It's the start line that counts! `11`
> * a list inside the quote
> * with two items `14`
>
> Still the same block quote, but another paragraph `16`

1. List item `18`
2. Nested list
   * item
   * another item `21`
3. List item with a nested `22`
   > block quote `23`

| Table `25` | Columns |
| ---------- | ------- |
| ?          | ! `27`  |

Paragraph with <p>inline HTML</p> `29`

Setext
heading `31`
------------

Paragraph with [ref] to a link reference definition.

[ref]: /url (37)
