import sys
import re

# Temporary solution for string/unicode in py2 vs py3
if sys.version >= '3':
    basestring = str


class TypedList(list):
    """Strongly typed list

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
        if isinstance(types, basestring) or not hasattr(types, '__iter__'):
            self._types = (types,)
        else:
            self._types = types
        tset = set([type(t) for t in self._types])
        
        self._null = null
        if len(tset) == 1:
            tset = tset.pop()
            self.__enforceType = self.__selectEnforcementMethod(tset)
        else:
            self.__enforceType = self.__enforceTypeMixed
        if init:
            self.extend(init)
        elif null is False:
            raise TypeError("This list must not be empty")

    def __repr__(self):
        return "hah"


    def __selectEnforcementMethod(self, t):
        if issubclass(t, (basestring, int)):
            return self.__enforceTypeStrInt
        elif t is re._pattern_type:
            return self.__enforceTypePattern
        elif isinstance(t, type):
            return self.__enforceTypeClass

    def __enforceTypeMixed(self, items):
        res = []
        for item in items:
            et = self.__selectEnforcementMethod(type(item))
            res.append(et((item,)))
        if all(res):
            return
        raise TypeError('This list accepts only elements: %s' %
                        ', '.join([str(t) for t in self._types]))

    def __enforceTypeStrInt(self, items):
        if all(i in self._types for i in items):
            return True
        raise TypeError('This list accepts only elements: %s' %
                        ', '.join([str(t) for t in self._types]))

    def __enforceTypeClass(self, items):
        if all(isinstance(i, self._types) for i in items):
            return True
        raise TypeError('This list accepts only elements: %s' %
                        ', '.join([str(t) for t in self._types]))

    def __enforceTypePattern(self, items):
        if all(any(j.match(i) for j in self._types) for i in items):
            return True
        raise TypeError('This list accepts only elements: %s' %
                        ', '.join([str(t) for t in self._types]))

    def append(self, item):
        self.__enforceType((item,))
        return super(TypedList, self).append(item)

    def insert(self, pos, item):
        self.__enforceType((item,))
        return super(TypedList, self).insert(pos, item)

    def extend(self, items):
        self.__enforceType(items)
        return super(TypedList, self).extend(items)

    def pop(self, key=-1):
        if self._null is False and len(self) == 1:
            raise TypeError("This list must not be empty")
        return super(TypedList, self).pop(key)

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
