import json
import pyast
from collections import OrderedDict

import sys

if sys.version >= '3':
    basestring = str
else:
    pass 

def _dump_node(node, name=None, indent=0):
    if node is None:
        return None
    if isinstance(node, (int, bool, basestring)):
        return node


    struct = OrderedDict({'type': None})
    if isinstance(node, pyast.Node):
        struct['type'] = node
        for field in node._fields:
            struct[field] = _dump_node(getattr(node, field))
    elif isinstance(node, list):
        struct = []
        for elem in node:
            struct.append(_dump_node(elem))
    elif isinstance(node, dict):
        struct = {}
        for key, elem in node.items():
            struct[key] =_dump_node(elem)
    return struct

def dump(ast):
    struct = _dump_node(ast)
    o = json.dumps(struct, indent=2)
    return o
