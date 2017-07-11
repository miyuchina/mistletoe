def check_equal(test, t, o):
    if hasattr(t, 'children') and hasattr(o, 'children'):
        [ check_equal(test, tc, to) for tc, to in zip(t.children, o.children) ]
    elif hasattr(t, 'language') and hasattr(o, 'language'):
        test.assertEqual((t.language, t.content), (o.language, o.content))
    elif hasattr(t, 'content') and hasattr(o, 'content'):
        test.assertEqual(t.content, o.content)
    elif hasattr(t, 'name') and hasattr(o, 'name'):
        test.assertEqual((t.name, t.target), (o.name, o.target))
    elif (type(t).__name__ == 'Separator'
            and type(o).__name__ == 'Separator'):
        test.assertTrue(True)
    else:
        raise Exception('Undefined token type comparison: '
                        + type(t).__name__ + ', ' + type(o).__name__)

def check_unequal(test, t, o):
    if hasattr(t, 'children') and hasattr(o, 'children'):
        [ check_equal(test, tc, to) for tc, to in zip(t.children, o.children) ]
    elif hasattr(t, 'language') and hasattr(o, 'language'):
        test.assertNotEqual((t.language, t.content), (o.language, o.content))
    elif hasattr(t, 'content') and hasattr(o, 'content'):
        test.assertNotEqual(t.content, o.content)
    elif hasattr(t, 'name') and hasattr(o, 'name'):
        test.assertNotEqual((t.name, t.target), (o.name, o.target))
    else:
        raise Exception('Undefined token type comparison: '
                        + type(t).__name__ + ', ' + type(o).__name__)

