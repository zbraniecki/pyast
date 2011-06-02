####
#
# The debug mode allows user to enforce type checks in AST based classes
# 
# The cost is ~2x slower performance on operations around AST classes.
#
####
DEBUG = True

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
        if types.__class__ in (type, str):
            types = (types,)
        return {'types': types,
                'guard_type': 'str' if isinstance(types[0], basestring) else 'class',
                'field_cls': cls,
                'null': null,
                'default': default,
                '_counter': basefield._counter}


class field(basefield):
    """Single Node field
 
    example:

    class Foo(ast.Node)
        id = ast.field(Identifier)
        prefix = ast.field(Prefix, null=True)
        computed = ast.field(bool, default=True)

    """
    if DEBUG:
        @classmethod
        def init(cls, name, val, guard):
            cls._validate_set(name, val, guard)
            return val
    else:
        @classmethod
        def init(cls, name, val, guard):
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
    if DEBUG:
        @classmethod
        def init(cls, name, val, guard):
            val = TypedList(val,
                            guard['types'],
                            null=guard['null'])
            return val
    else:
        @classmethod
        def init(cls, name, val, guard):
            return list(val) if val else []

    @classmethod
    def _validate_set(cls, name, val, guard):
        if val is None and guard['null'] is True:
            return
        if hasattr(val, '__iter__'):
            if not all(isinstance(i, guard['types']) for i in val):
                raise TypeError('Element must be one of %r' % guard['types'])
        else:
            raise TypeError('Element must be a sequence')

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
    _type = 'class' # class | str

    def __init__(self, init, types, null=False):
        super(TypedList, self).__init__()
        self._types = types
        self._null = null
        self._type = "str" if isinstance(types[0], basestring) else "class"
        if init:
            self.extend(init)
        elif null is False:
            raise TypeError("This list must not be empty")

    def __enforceType(self, items):
        if not hasattr(items, '__iter__'):
            items = (items,)
        if self._type is "str":
            if all(i in self._types for i in items):
                return
        else:
            if all(isinstance(i, self._types) for i in items):
                return
        raise TypeError('Elements must be one of %r' %
                        ','.join(map(str, self._types)))

    def append(self, item):
        self.__enforceType(item)
        return super(TypedList, self).append(item)

    def insert(self, pos, item):
        self.__enforceType(item)
        return super(TypedList, self).insert(pos, item)

    def extend(self, items):
        self.__enforceType(items)
        return super(TypedList, self).extend(items)
    set = extend

    def pop(self):
        if self._null is False and len(self)==1:
            raise TypeError("This list must not be empty")
        return super(TypedList, self).pop()

    def __delitem__(self, key):
        if self._null is False and len(self)==1:
            raise TypeError("This list must not be empty")
        list.__delitem__(self, key)

    def __setitem__(self, key, value):
        self.__enforceType(value)
        list.__setitem__(self, key, value)

    def __setslice__(self, i, j, sequence):
        self.__enforceType(sequence)
        list.__setslice__(self, i, j, sequence)

    def __delslice__(self, i, j):
        if self._null is False and len(self)<=j-i:
            raise TypeError("This list must not be empty")
        list.__delslice__(self, i, j)

class NodeBase(type):
    """ Metaclass for AST Nodes
    Verifies the syntax of the declarative field syntax
    """
    def __init__(cls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, NodeBase)]
        if not parents:
            return
        guards = {}
        for k,v in attrs.items():
            if k.startswith('_') or hasattr(v, '__call__'):
                continue
            if not issubclass(v['field_cls'], basefield):
                raise TypeError('Field type must be a subclass of basefield')
            if not all(isinstance(i, (type, str)) for i in v['types']):
                raise TypeError('Field types must be python types or strings')
            guards[k] = v
        fields = [i[0] for i in sorted(guards.items(),
                                       key=lambda x: x[1]['_counter'])]
        setattr(cls, '_fields', fields)
        setattr(cls, '_guards', guards)

class Node(object):
    """Basic AST Node

    Any Node should subclass from this one
    """
    __metaclass__ = NodeBase

    def __init__(self, *args, **kwargs):
        guards = self.__class__._guards
        attrs = self.__class__._fields
        args = list(args)

        for name in attrs:
            val = None
            if name in kwargs:
                val = kwargs.pop(name)
            else:
                try:
                    val = args.pop(0)
                except IndexError:
                    val = guards[name]['default']
            val = guards[name]['field_cls'].init(name, val, guards[name])
            object.__setattr__(self, name, val)

    if DEBUG:
        def __setattr__(self, name, val):
            if name in self._fields:
                val = self._guards[name]['field_cls'].init(name,
                                                          val,
                                                          self._guards[name])
            object.__setattr__(self, name, val)


        def __delattr__(self, name):
            if name in self._fields:
                raise Exception("Cannot remove Node's fields")
            object.__delattr__(self, name)


