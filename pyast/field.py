import sys
import re as regexp
from .typedlist import TypedList

# Temporary solution for string/unicode in py2 vs py3
if sys.version >= '3':
    basestring = str

# we redefine to make pyast.re() a proper field
def re(s):
    return regexp.compile(s)


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

    _guard_types = {
        'str': lambda x: isinstance(x, basestring),
        'class': lambda x: isinstance(x, type),
        'pattern': lambda x: isinstance(x, regexp._pattern_type),
    }

    def __new__(cls, types, null=False, default=None):
        basefield._counter += 1
        if isinstance(types, (type, basestring, regexp._pattern_type)):
            types = (types,)
        guard_type = None
        for k,v in cls._guard_types.items():
            if v(types[0]):
                guard_type = k
                break
        return {'types': types,
                'guard_type': guard_type,
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
            if guard['guard_type'] == 'str':
                if val in guard['types']:
                    return
            elif guard['guard_type'] == 'pattern':
                for guardt in guard['types']:
                    if guardt.match(val):
                        return
            else:
                if isinstance(val, guard['types']):
                    return
        allowed = []
        for i in guard['types']:
            if isinstance(i, regexp._pattern_type):
                allowed.append(i.pattern)
            else:
                allowed.append(str(i))
        raise TypeError('Element %s must be one of %r' %
                        (name, ','.join(allowed)))


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
        try:
            return TypedList(guard['types'],
                             val,
                             null=guard['null'])
        except TypeError as e:
            raise TypeError('Error in field "%s":\n %s' % (
                name,
                str(e)))

    @classmethod
    def _validate_set(cls, name, val, guard):
        if val is None and guard['null'] is True:
            return
        if hasattr(val, '__iter__'):
            if not all(isinstance(i, guard['types']) for i in val):
                raise TypeError('Element must be one of %r' % guard['types'])
        else:
            raise TypeError('Element must be a sequence')
