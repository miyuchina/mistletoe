from collections import namedtuple

TraverseResult = namedtuple('TraverseResult', ['node', 'parent', 'depth'])


def traverse(source, klass=None, depth=None, include_source=False):
    """Traverse the syntax tree, recursively yielding children.

    Args:

        source: The source syntax token
        klass: filter children by a certain token class
        depth (int): The depth to recurse into the tree
        include_source (bool): whether to first yield the source element

    Yields:
        A container for an element, its parent and depth
    """
    current_depth = 0
    if include_source:
        yield TraverseResult(source, None, current_depth)
    next_children = [(source, c) for c in getattr(source, 'children', [])]
    while next_children and (depth is None or current_depth > depth):
        current_depth += 1
        new_children = []
        for parent, child in next_children:
            if klass is None or issubclass(child, klass):
                yield TraverseResult(child, parent, current_depth)
            new_children.extend(
                [(child, c) for c in getattr(child, 'children', [])]
            )
        next_children = new_children
