import unittest

import pyast as ast


class BaseASTTestCase(unittest.TestCase):
    def test_basic_template(self):
        class Entity(ast.Node):
            _debug = True
            id = ast.field(str)
            value = ast.field(str)

            _template = '<%(id)s %(value)s>'
        
        e = Entity('foo', 'val')
       
        self.assertEqual(str(e), '<foo val>')

    def test_nested_template(self):
        class Value(ast.Node):
            content = ast.field(str)

            _template = '"%(content)s"'

        class Entity(ast.Node):
            _debug = True
            id = ast.field(str)
            value = ast.field(Value)

            _template = '<%(id)s %(value)s>'
        
        e = Entity('foo', Value('val'))
       
        self.assertEqual(str(e), '<foo "val">')

    def test_nested_template_callable(self):
        class Value(ast.Node):
            content = ast.field(str)

            @property
            def _template(self):
                return '"%(content)s"'

        class Entity(ast.Node):
            _debug = True
            id = ast.field(str)
            value = ast.field(Value)

            _template = '<%(id)s %(value)s>'
        
        e = Entity('foo', Value('val'))
       
        self.assertEqual(str(e), '<foo "val">')

    def test_nested_repr(self):
        class Value(ast.Node):
            content = ast.field(str)

            _template = '"%(content)s"'
            
            def __repr__(self):
                content = self.content.replace('"', '\\"')
                return super(Value, self).__repr__(fields={'content': content})

        class Entity(ast.Node):
            _debug = True
            id = ast.field(str)
            value = ast.field(Value)

            _template = '<%(id)s %(value)s>'
        
        e = Entity('foo', Value('val"val2'))
       
        self.assertEqual(str(e), '<foo "val\\"val2">')

    def test_null_value(self):
        class Value(ast.Node):
            content = ast.field(str)

            _template = '"%(content)s"'
            
            def __repr__(self):
                content = self.content.replace('"', '\\"')
                return super(Value, self).__repr__(fields={'content': content})

        class Entity(ast.Node):
            _debug = True
            id = ast.field(str)
            value = ast.field(Value, null=True)

            @property
            def _template(self):
                if self.value:
                    return '<%(id)s %(value)s>'
                return '<%(id)s>'
        
        e = Entity('foo')
       
        self.assertEqual(str(e), '<foo>')

        e.value = Value("hey")

        self.assertEqual(str(e), '<foo "hey">')

    def test_empty_list(self):
        class KVP(ast.Node):
            key = ast.field(str)
            value = ast.field(str)

        class Hash(ast.Node):
            _debug = True
            content = ast.seq(KVP, null=True)

            @property
            def _template(self):
                if len(self.content):
                    return "{\n%(content)s\n}"
                return "{}"

        e = Hash()
       
        self.assertEqual(str(e), '{}')

    def test_list(self):
        class KVP(ast.Node):
            key = ast.field(str)
            value = ast.field(str)

        class Hash(ast.Node):
            _debug = True
            content = ast.seq(KVP, null=True)

            @property
            def _template(self):
                if len(self.content):
                    return "{\n%(content)s\n}"
                return "{}"

        e = Hash([KVP('key1', 'val1')])
       
        self.assertEqual(str(e), '{"key1": "val1"}')

if __name__ == '__main__':
    unittest.main()
