import sys
from .typedlist import TypedList

# Temporary solution for string/unicode in py2 vs py3
if sys.version >= '3':
    basestring = str

class basefield(object):
    """Base abstract class for AST field pseudoclasses

    The pseudoclasses are used to build fields for AST Nodes in declarative
    way.
    Example:

    class Foo(ast.Node)
        id = ast.field(Identifier)
        attrs = ast.seq(Statement)

    Attributes:
        types - single type of a tuple of types
        null - can the field or sequence be empty
        default - what is the default value of the field/sequence

    Types may be either classes or strings. If types are strings then the value
    of the field may be only a string matching one of the types.

    examples:

        ast.seq((Identifier, Literal))
        ast.seq(Expression)
        ast.field(("+","-","="))
    """
    _counter = 0

    def __new__(cls, types, null=False, default=None):
        basefield._counter += 1
        if isinstance(types, (type, basestring)):
            types = (types,)
        return {'types': types,
                'guard_type': 'str' if isinstance(types[0],
                                                  basestring) else 'class',
                'field_cls': cls,
                'null': null,
                'default': [] if (default is None and
                                       issubclass(cls, seq)) else default,
                '_counter': basefield._counter}


class field(basefield):
    """Single Node field

    example:

    class Foo(ast.Node)
        id = ast.field(Identifier)
        prefix = ast.field(Prefix, null=True)
        computed = ast.field(bool, default=True)

    """
    @classmethod
    def init(cls, name, val, guard):
        cls._validate_set(name, val, guard)
        return val

    @classmethod
    def _validate_set(self, name, val, guard):
        if val is None:
            if guard['null'] is False:
                raise TypeError('Element %s must not be empty' % name)
            return
        else:
            if guard['guard_type'] is 'str':
                if val in guard['types']:
                    return
            else:
                if isinstance(val, guard['types']):
                    return
        raise TypeError('Element %s must be one of %r' %
                        (name, ','.join(map(str, guard['types']))))


class seq(basefield):
    """Node field sequence

    example:

    class Foo(ast.Node)
        id = ast.seq(Identifier)
        prefix = ast.seq((Prefix, Literal), null=True)
        computed = ast.seq(bool, default=True)


    """
    @classmethod
    def init(cls, name, val, guard):
        return TypedList(guard['types'],
                         val,
                         null=guard['null'])

    @classmethod
    def _validate_set(cls, name, val, guard):
        if val is None and guard['null'] is True:
            return
        if hasattr(val, '__iter__'):
            if not all(isinstance(i, guard['types']) for i in val):
                raise TypeError('Element must be one of %r' % guard['types'])
        else:
            raise TypeError('Element must be a sequence')

