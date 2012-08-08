import json
import pyast
from collections import OrderedDict

def _dump_node_name(node):
    return node.__class__.__name__.lower()

def _dump_node(node, name=None, indent=0):
    if isinstance(node, str):
        return node
    elif isinstance(node, bool):
        return node

    struct = OrderedDict({'type': None})
    if isinstance(node, pyast.Node):
        struct['type'] = _dump_node_name(node)
        for field in node._fields:
            struct[field] = _dump_node(getattr(node, field))
    elif isinstance(node, pyast.TypedList):
        struct = []
        for elem in node:
            struct.append(_dump_node(elem))
    elif isinstance(node, pyast.TypedDict):
        struct = {}
        for elem, key in node.items():
            struct[key] =_dump_node(elem)
    return struct

def dump(ast):
    struct = _dump_node(ast)
    o = json.dumps(struct, indent=2)
    return o
