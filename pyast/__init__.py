from .field import field, seq, re
from .node import Node

def _dump_node(node, name=None, indent=0):
    tree = []
    if isinstance(node, str):
        cl = "%s=\"%s\"" % (node.__class__.__name__, node)
    elif isinstance(node, bool):
        cl = "%s=%s" % (node.__class__.__name__, node)
    elif isinstance(node, int):
        cl = "%s=%s" % (node.__class__.__name__, node)
    else:
        cl = node.__class__.__name__
    tree.append((indent, "%s[%s]" % (".%s" % name if name else "", cl)))
    indent += 2
    if isinstance(node, str):
        #tree.append((indent, '"%s"' % node))
        return tree
    if isinstance(node, int):
        return tree
    if isinstance(node, bool):
        return tree
    elif node is None:
        return []
    for i in node._fields:
        field = getattr(node, i)
        if isinstance(field, list):
            tree.append((indent, ".%s" % i))
            tree.extend(_dump_list(field, indent=indent+2))
        else:
            tree.extend(_dump_node(field, name=i, indent=indent))
    return tree

def _dump_list(tList, indent=0):
    tree = []
    for item in tList:
        tree.extend(_dump_node(item, indent=indent))
    return tree


def dump(ast):
    tree = _dump_node(ast)
    string = ""
    for (indent, i) in tree:
        string += "%s%s\n" % (indent*" ", i)
    return string
