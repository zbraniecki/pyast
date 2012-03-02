from .field import field, seq, re
from .node import Node

def _dump_node(node, indent=0):
    tree = []
    tree.append((indent, "[%s]" % node.__class__.__name__))
    indent += 2
    if isinstance(node, str):
        tree.append((indent, '"%s"' % node))
        return tree
    elif node is None:
        return
    for i in node._fields:
        tree.append((indent, ".%s" % i))
        field = getattr(node, i)
        if isinstance(field, list):
            tree.extend(_dump_list(field, indent=indent+2))
        else:
            tree.extend(_dump_node(field, indent=indent+2))
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
