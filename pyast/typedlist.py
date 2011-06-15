import sys
import re

# Temporary solution for string/unicode in py2 vs py3
if sys.version >= '3':
    basestring = str


class TypedList(list):
    """Strongly types list

    All elements of the list must be one of the given types.

    Attributes:
        init - initial values
        types - allowed types
        null - can the list be null

    Types may be either classes or strings. If types are strings then the value
    of the field may be only a string matching one of the types.

    examples:

        TypedList([Identifier(), Identifier()], (Identifier, Literal))
        TypedList([], Expression, null=True)
        ast.field(["+","-","+"], ("+","-","="))
    """
    _type = 'class'  # class | str | pattern

    def __init__(self, types, init=None, null=False):
        super(TypedList, self).__init__()
        self._types = types
        self._null = null
        if isinstance(types[0], basestring):
            self.__enforceType = self.__enforceTypeStr
        elif isinstance(types[0], re._pattern_type):
            self.__enforceType = self.__enforceTypePattern
        else:
            self.__enforceType = self.__enforceTypeClass
        if init:
            self.extend(init)
        elif null is False:
            raise TypeError("This list must not be empty")

    def __enforceTypeStr(self, items):
        if all(i in self._types for i in items):
            return
        raise TypeError('This list accepts only strings of value: %s' %
                        ', '.join(self._types))

    def __enforceTypeClass(self, items):
        if all(isinstance(i, self._types) for i in items):
            return
        raise TypeError('This list accepts only elements of types: %s' %
                        ', '.join([str(i.__name__) for i in self._types]))

    def __enforceTypePattern(self, items):
        if all(j.match(i) for j in self._types for i in items):
            return
        raise TypeError('This list accepts only elements that match: %s' %
                        ', '.join([i.pattern for i in self._types]))

    def append(self, item):
        self.__enforceType((item,))
        return super(TypedList, self).append(item)

    def insert(self, pos, item):
        self.__enforceType((item,))
        return super(TypedList, self).insert(pos, item)

    def extend(self, items):
        self.__enforceType(items)
        return super(TypedList, self).extend(items)

    def pop(self):
        if self._null is False and len(self) == 1:
            raise TypeError("This list must not be empty")
        return super(TypedList, self).pop()

    def __delitem__(self, k):
        if self._null is False:
            if type(k) is slice:
                absslice = k.indices(len(self))
                if absslice[1] - absslice[0] >= len(self):
                    raise TypeError("This list must not be empty")
            elif len(self) == 1:
                raise TypeError("This list must not be empty")
        return list.__delitem__(self, k)

    def __setitem__(self, key, value):
        self.__enforceType(value if hasattr(value, '__iter__') else (value,))
        return list.__setitem__(self, key, value)

    def __setslice__(self, i, j, sequence):
        self.__enforceType(sequence)
        return list.__setslice__(self, i, j, sequence)

    def __delslice__(self, i, j):
        absslice = slice(i, j).indices(len(self))
        if self._null is False and absslice[1] - absslice[0] >= len(self):
            raise TypeError("This list must not be empty")
        return list.__delslice__(self, i, j)
