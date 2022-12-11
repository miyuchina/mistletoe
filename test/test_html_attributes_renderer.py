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
![foo](https://i.creativecommons.org/l/by-sa/4.0/80x15.png "toof")

${ > class:btn-link, onclick:event.preventDefault();console.log(this,'button clicked');}
[some link](https://i.creativecommons.org/l/by-sa/4.0/80x15.png "toof")\
            """
        block_token.HTMLAttributes.enable_auto_ids = True
        html = markdown(txt, HTMLAttributesRenderer)
        output = '<h1 class="foobar" id="mistletoe-is-awesome" tabindex="1">Mistletoe is Awesome</h1>\n<ul id="todos" tabindex="100">\n<li class="list-item" tabindex="1">Push Code</li>\n<li class="list-item" tabindex="1">Get Groceries\n<ul id="todos-0" tabindex="1">\n<li class="list-item" tabindex="1">Veggies</li>\n<li class="list-item" tabindex="1">Fruits\n<ul id="todos-0-1" tabindex="1">\n<li class="list-item" tabindex="1">apples</li>\n<li class="list-item" tabindex="1">oranges</li>\n</ul>\n</li>\n</ul>\n</li>\n<li class="list-item" tabindex="1">Hang up the mistletoe</li>\n</ul>\n<p class="img-sm" tabindex="1"><img src="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" alt="foo" title="toof" tabindex="1" /></p>\n<p tabindex="1"><a href="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" title="toof" class="btn-link" onclick="event.preventDefault();console.log(this,\'button clicked\');" tabindex="1">some link</a></p>\n'
        self.assertEqual(html, output)

t = TestHTMLAttributes()
t.test_document()