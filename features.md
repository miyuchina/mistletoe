HTMLAttributesRenderer
----------------------

This feature allows you to write Markdown that will render 508 compliant html attributes.


**HTMLAttributesRenderer Block syntax**

Contents within the following characters `${...}` will describe how the HTMLAttributesRenderer will process and include attributes.

`${ ..................... }`

The content string is partitioned by the optional ` > ` character (whitespace included) will separate parent attributes from child attributes. Attributes defined on the left will apply to root parent element and the right side applies to children.

`${ id:some-parent > class:our-code our-love }`

Multiple attribute pairs are delimited using comma space. `, `

`${ class:our-code our-love, aria-label:spread-love }`

Multiple attributes values are delimited using a single space. ` `

`${ class:our-code our-love }`

example:


**How to Use HTMLAttributesRenderer**

```python
import mistletoe
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

${ > class:btn-link, onclick:event.preventDefault();console.log(this,'button clicked');}
[some link](https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg "toof")\
"""

# Optional: Configure HTMLAttributesRenderer
HTMLAttributesRenderer.configure({...})

# Render the markdown into html
rendered = mistletoe.markdown(txt, HTMLAttributesRenderer)
```

OUTPUT

```html
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
<p class="img-sm" tabindex="1">
    <img src="https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg" alt="foo" title="toof" tabindex="1" />
</p>
<p tabindex="1">
    <a href="https://cdn.rawgit.com/miyuchina/mistletoe/master/resources/logo.svg" title="toof" class="btn-link"
        onclick="event.preventDefault();console.log(this,'button clicked');" tabindex="1">some link</a>
</p>
```
