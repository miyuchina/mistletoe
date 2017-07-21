def check_equal(test, t, o):
    if hasattr(t, 'children') and hasattr(o, 'children'):
        [ check_equal(test, tc, to) for tc, to in zip(t.children, o.children) ]
    elif hasattr(t, 'language') and hasattr(o, 'language'):
        test.assertEqual((t.language, t.content), (o.language, o.content))
    elif hasattr(t, 'content') and hasattr(o, 'content'):
        test.assertEqual(t.content, o.content)
    elif hasattr(t, 'src') and hasattr(o, 'src'):
        test.assertEqual((t.src, t.alt, t.title), (o.src, o.alt, o.title))
    elif hasattr(t, 'alt') and hasattr(o, 'alt'):
        test.assertEqual((t.alt, t.target), (o.alt, o.target))
    elif hasattr(t, 'name') and hasattr(o, 'name'):
        test.assertEqual((t.name, t.target), (o.name, o.target))
    elif hasattr(t, 'target') and hasattr(o, 'target'):
        [ check_equal(test, tc, to) for tc, to in zip(t.children, o.children) ]
        test.assertEqual(t.target, o.target)
    elif (type(t).__name__ == 'Separator'
            and type(o).__name__ == 'Separator'):
        test.assertTrue(True)
    else:
        raise Exception('Undefined token type comparison: '
                        + type(t).__name__ + ', ' + type(o).__name__)
