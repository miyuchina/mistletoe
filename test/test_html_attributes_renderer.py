from unittest import TestCase


class TestHTMLAttributes(TestCase):

    def test_document(self):
        from mistletoe import markdown, block_token
        from mistletoe.html_attributes_renderer import HTMLAttributesRenderer

        txt = """\
${class:foobar}
# Mistletoe is Awesome

${id:todos, tabindex:100 > class:list-item}
- Push Code
- Get Groceries
    - Veggies
    - Fruits
        - apples
        - oranges
- Hang up the mistletoe

${class:img-sm}
![foo](https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg "toof")

${ > class:btn-link, aria-label:Kiss Me under the mistle toe}
[some link](https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg "toof")\
            """
        block_token.HTMLAttributes.configure({"enable_auto_ids": True})
        html = markdown(txt, HTMLAttributesRenderer)
        output = """\
<h1 class="foobar" id="mistletoe-is-awesome" tabindex="1">Mistletoe is Awesome</h1>
<ul id="todos" tabindex="100">
<li class="list-item" tabindex="1">Push Code</li>
<li class="list-item" tabindex="1">Get Groceries
<ul id="todos-0" tabindex="1">
<li class="list-item" tabindex="1">Veggies</li>
<li class="list-item" tabindex="1">Fruits
<ul id="todos-0-1" tabindex="1">
<li class="list-item" tabindex="1">apples</li>
<li class="list-item" tabindex="1">oranges</li>
</ul>
</li>
</ul>
</li>
<li class="list-item" tabindex="1">Hang up the mistletoe</li>
</ul>
<p class="img-sm" tabindex="1"><img src="https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg" alt="foo" title="toof" tabindex="1" /></p>
<p tabindex="1"><a href="https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg" title="toof" class="btn-link" aria-label="Kiss Me under the mistle toe" tabindex="1">some link</a></p>
"""
        self.assertEqual(html, output)

t = TestHTMLAttributes()
t.test_document()