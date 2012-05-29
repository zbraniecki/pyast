import sys
import re

# Temporary solution for string/unicode in py2 vs py3
if sys.version >= '3':
    basestring = str


class TypedDict(dict):
    """Strongly typed dict

    All elements of the dict must be one of the given types.

    Attributes:
        init - initial values
        types - allowed types
        null - can the list be null

    Types may be either classes or strings. If types are strings then the value
    of the field may be only a string matching one of the types.

    examples:

        TypedDict([Identifier(), Identifier()], (Identifier, Literal))
        TypedDict([], Expression, null=True)
        ast.field(["+","-","+"], ("+","-","="))
    """
    _type = 'class'  # class | str | pattern

    def __init__(self, types, init=None, null=False):
        super(TypedDict, self).__init__()
        self._types = types
        self._null = null
        if isinstance(types, basestring):
            self.__enforceType = self.__enforceTypeStr
        elif isinstance(types, re._pattern_type):
            self.__enforceType = self.__enforceTypePattern
        else:
            if not hasattr(types, '__iter__'):
                types = (types,)
            self.__enforceType = self.__enforceTypeClass
        if init:
            for key, value in init.items():
                self.__setitem__(key, value)
        elif null is False:
            raise TypeError("This list must not be empty")

    def __enforceTypeStr(self, items):
        if all(i in self._types for i in items):
            return
        raise TypeError('This dict accepts only strings of value: %s' %
                        ', '.join(self._types))

    def __enforceTypeClass(self, items):
        if all(isinstance(i, self._types) for i in items):
            return
        raise TypeError('This dict accepts only elements of types: %s' %
                        ', '.join([str(i.__name__) for i in self._types]))

    def __enforceTypePattern(self, items):
        if all(j.match(i) for j in self._types for i in items):
            return
        raise TypeError('This dict accepts only elements that match: %s' %
                        ', '.join([i.pattern for i in self._types]))

    def pop(self):
        if self._null is False and len(self) == 1:
            raise TypeError("This dict must not be empty")
        return super(TypedDict, self).pop()

    def __delitem__(self, k):
        if self._null is False and len(self) == 1:
            raise TypeError("This dict must not be empty")
        return super(TypedDict, self).__delitem__(k)

    def __setitem__(self, key, value):
        self.__enforceType(value if hasattr(value, '__iter__') else (value,))
        return super(TypedDict, self).__setitem__(key, value)

