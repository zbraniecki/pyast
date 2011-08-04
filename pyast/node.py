import sys
import re
from .field import basefield

class NodeBase(type):
    """ Metaclass for AST Nodes
    Verifies the syntax of the declarative field syntax
    """
    def __new__(cls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, NodeBase)]
        if not parents:
            return type.__new__(cls, name, bases, attrs)
        guards = {}
        for base in bases:
            if isinstance(base, NodeBase) and hasattr(base, '_guards'):
                guards.update(base._guards)
        for k, v in attrs.items():
            if k.startswith('_') or hasattr(v, '__call__'):
                continue
            if not issubclass(v['field_cls'], basefield):
                raise TypeError('Field type must be a subclass of basefield')
            if not all(isinstance(i, (type,
                                      str,
                                      re._pattern_type)) for i in v['types']):
                raise TypeError('Field types must be python types or strings')
            guards[k] = v
        fields = [i[0] for i in sorted(guards.items(),
                                       key=lambda x: x[1]['_counter'])]
        attrs['_guards'] = guards
        attrs['_fields'] = fields
        if not '_abstract' in attrs.keys():
            attrs['_abstract'] = False
        return type.__new__(cls, name, bases, attrs)

# Temporary solution for metaclass in py2 vs py3
if sys.version >= '3':
    TempNode = NodeBase("NodeBase", (object,), {})
else:
    TempNode = object


### Consider DebugNode and OptNode and switch which one is used
class Node(TempNode):
    """Basic AST Node

    Any Node should subclass from this one
    """
    __metaclass__ = NodeBase

    ####
    #
    # The debug mode allows user to enforce type checks in AST based classes
    #
    # The cost is ~2x slower performance on operations around AST classes.
    #
    ####
    _debug = True

    def __init__(self, *args, **kwargs):
        key = 0
        if self._debug and self._abstract:
            raise TypeError('Class %s is abstract' % self.__class__.__name__)
        for name in self._fields:
            if name in kwargs:
                val = kwargs.pop(name)
            else:
                try:
                    val = args[key]
                    key += 1
                except IndexError:
                    val = self._guards[name]['default']
                    if hasattr(val, '__iter__'):
                        val = val[:]
            if self._debug:
                guards = self._guards
                val = guards[name]['field_cls'].init(name,
                                                     val,
                                                     guards[name])
                setattr(self.__class__, '__delattr__', self.__debug__delattr__)
                setattr(self.__class__, '__setattr__', self.__debug__setattr__)
                self.__debug__setattr__(name, val)
            else:
                object.__setattr__(self, name, val)

    def __debug__setattr__(self, name, val):
        if name in self._fields:
            val = self._guards[name]['field_cls'].init(name,
                                                      val,
                                                      self._guards[name])
        object.__setattr__(self, name, val)

    def __debug__delattr__(self, name):
        if name in self._fields:
            raise Exception("Cannot remove Node's fields")
        object.__delattr__(self, name)
