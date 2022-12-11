from unittest import TestCase, mock
from mistletoe.html_renderer import HTMLRenderer


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
        print(html)
        html = '<h1 class=foobar id=mistletoe-is-awesome>Mistletoe is Awesome</h1>\n<ul id=todos>\n<li>Item One</li>\n<li>Item Two</li>\n<li>Item Three</li>\n</ul>\n<p class=img-sm><img src="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" alt="foo" title="toof" /></p>\n<p><a href="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" title="toof" class=btn-link onclick=event.preventDefault();console.log(this,\'button clicked\');>some link</a></p>\n'
        output = '<h1 class=foobar id=mistletoe-is-awesome>Mistletoe is Awesome</h1>\n<ul id=todos>\n<li>Item One</li>\n<li>Item Two</li>\n<li>Item Three</li>\n</ul>\n<p class=img-sm><img src="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" alt="foo" title="toof" /></p>\n<p><a href="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" title="toof" class=btn-link onclick=event.preventDefault();console.log(this,\'button clicked\');>some link</a></p>\n'
        self.assertEqual(html, output)

t = TestHTMLAttributes()
t.test_document()