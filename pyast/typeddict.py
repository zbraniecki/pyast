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
            for key, value in init.items():
                self.__setitem__(key, value)
        elif null is False:
            raise TypeError("This dict must not be empty")

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
        raise TypeError('This dict accepts only elements: %s' %
                        ', '.join([str(t) for t in self._types]))

    def __enforceTypeStrInt(self, items):
        if all(i in self._types for i in items):
            return True
        raise TypeError('This dict accepts only elements: %s' %
                        ', '.join([str(t) for t in self._types]))

    def __enforceTypeClass(self, items):
        if all(isinstance(i, self._types) for i in items):
            return
        raise TypeError('This dict accepts only elements: %s' %
                        ', '.join([str(i.__name__) for i in self._types]))

    def __enforceTypePattern(self, items):
        if all(any(j.match(i) for j in self._types) for i in items):
            return
        raise TypeError('This dict accepts only elements: %s' %
                        ', '.join([i.pattern for i in self._types]))

    def pop(self, key, default=None):
        if self._null is False and len(self) == 1:
            raise TypeError("This dict must not be empty")
        return super(TypedDict, self).pop(key, default)

    def __delitem__(self, k):
        if self._null is False and len(self) == 1:
            raise TypeError("This dict must not be empty")
        return super(TypedDict, self).__delitem__(k)

    def __setitem__(self, key, value):
        self.__enforceType(value if hasattr(value, '__iter__') else (value,))
        return super(TypedDict, self).__setitem__(key, value)

