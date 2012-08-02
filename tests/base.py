import unittest

import pyast as ast


class BaseASTTestCase(unittest.TestCase):
    def test_basic_init(self):
        class Example(ast.Node):
            _debug = True
            field = ast.field(str, null=True)
            seq = ast.seq((str, int), null=True)
        
        e = Example()
        self.assertEqual(type(e), Example)
        self.assertEqual(e.field, None)
        self.assertEqual(len(e.seq), 0)

        e = Example(field="foo")
        self.assertEqual(type(e), Example)
        self.assertEqual(e.field, "foo")
        self.assertEqual(len(e.seq), 0)

        self.assertRaises(TypeError, Example, {'field':2})

        e = Example(seq=('a', 2))
        self.assertEqual(type(e), Example)
        self.assertEqual(e.field, None)
        self.assertEqual(len(e.seq), 2)
        self.assertEqual(e.seq[0], 'a')
        self.assertEqual(e.seq[1], 2)

        e = Example(seq=('a', 2), field="foo")
        e2 = Example(field="foo", seq=('a', 2))
        self.assertEqual(type(e), Example)
        self.assertEqual(len(e.seq), len(e2.seq))
        self.assertEqual(e.seq[0], e2.seq[0])
        self.assertEqual(e.seq[1], e2.seq[1])
        self.assertEqual(e.field, e2.field)

    def test_not_null(self):
        class Example(ast.Node):
            _debug = True
            field = ast.field(str, null=False)
            seq= ast.seq((str, int), null=False)

        self.assertRaises(TypeError, Example)
        self.assertRaises(TypeError, Example, field='foo')
        self.assertRaises(TypeError, Example, field=2)

        self.assertRaises(TypeError, Example, field= 2, seq=['a'])
        self.assertRaises(TypeError, Example, field='s', seq=[Example])
        self.assertRaises(TypeError, Example, seq=[2])
        self.assertRaises(TypeError, Example, field='s', seq=2)

        e = Example(field='s', seq=[2])

    def test_field(self):
        class Example(ast.Node):
            _debug = True
            field = ast.field(str, null=True)
        e = Example()
        self.assertRaises(TypeError, Example, {'field': 2})
        
        e = Example(field="s")
        self.assertEqual(e.field, "s")

        e.field = "hola"
        self.assertEqual(e.field, "hola")

        self.assertRaises(TypeError, e.__setattr__, 'field', 2)
        self.assertRaises(TypeError, e.__setattr__, 'field', False)
        self.assertRaises(TypeError, e.__setattr__, 'field', 0)
        e.field = None
       
        self.assertRaises(Exception, e.__delattr__, 'field')

        e = Example(None)

        class Example(ast.Node):
            _debug = True
            field = ast.field(str, null=False)

        self.assertRaises(TypeError, Example, {})
        self.assertRaises(TypeError, Example, {'field': 2})
        
        e = Example(field="s")
        self.assertEqual(e.field, "s")

        e.field = "hola"
        self.assertEqual(e.field, "hola")

        self.assertRaises(TypeError, e.__setattr__, 'field', 2)
        self.assertRaises(TypeError, e.__setattr__, 'field', None)
        self.assertRaises(TypeError, e.__setattr__, 'field', False)
        self.assertRaises(TypeError, e.__setattr__, 'field', 0)

        self.assertRaises(Exception, e.__delattr__, 'field')

    def test_seq(self):
        class Example(ast.Node):
            _debug = True
            seq = ast.seq(str, null=True)

        e = Example()
        self.assertEqual(len(e.seq), 0)
        self.assertRaises(TypeError, e.__setattr__, seq=None)

        self.assertRaises(TypeError, Example, (2,))
        e = Example(None)
        e.seq = []
        
        e = Example(['a','b'])
        self.assertEqual(len(e.seq), 2)
        self.assertEqual(e.seq[1], 'b')
        
        e.seq.pop()
        e.seq.pop()
        
        self.assertEqual(len(e.seq), 0)

        e.seq = ['a','b']
        del e.seq[0:2]

        e.seq = ['a']
        del e.seq[0]

        class Example(ast.Node):
            seq = ast.seq(str, null=False)

        self.assertRaises(TypeError, Example)
        self.assertRaises(TypeError, Example, [2])

        e = Example(['a','b'])

        self.assertRaises(TypeError, e.__setattr__, 'seq', None)
        self.assertRaises(TypeError, e.__setattr__, 'seq', [])

        e.seq = ['a', 'b', 'c']

        self.assertEqual(e.seq[2], 'c')

        self.assertRaises(TypeError, e.__setattr__, 'seq', ['a', 3, 'c'])

        e.seq.append('d')
        self.assertEqual(e.seq[3], 'd')

        self.assertRaises(TypeError, e.seq.append, 3)

        e.seq.insert(0, 'e')
        self.assertEqual(e.seq[0], 'e')

        self.assertRaises(TypeError, e.seq.insert, 0, 2)

        e.seq = ['a']
        self.assertRaises(TypeError, e.seq.pop)

        self.assertRaises(TypeError, e.seq.__delitem__, 0)

        e.seq[0] = 'd'

        self.assertRaises(TypeError, e.seq.__setitem__, 0, 2)

        e.seq = ['a','b','c']
        e.seq[0:2] = ['d','f']
        self.assertEqual(e.seq[1], 'f')

        self.assertRaises(TypeError, e.seq.__setslice__, 0, 2, [2, 'p'])

        del e.seq[0:2]

        self.assertEqual(len(e.seq), 1)
        self.assertRaises(TypeError, e.seq.__delslice__, 0, 1)
    
    def test_dict(self):
        class Example(ast.Node):
            _debug = True
            seq = ast.dict(str, null=True)

        e = Example()
        self.assertEqual(len(e.seq), 0)
        self.assertRaises(TypeError, e.__setattr__, seq=None)

        self.assertRaises(TypeError, Example, {'a':2})
        e = Example(None)
        e.seq = []
        
        e = Example({'a':'a','b':'b'})
        self.assertEqual(len(e.seq), 2)
        self.assertEqual(e.seq['a'], 'a')
        
        e.seq.pop('a')
        e.seq.pop('b')
        
        self.assertEqual(len(e.seq), 0)

        e.seq = {'a':'a', 'b':'b'}
        del e.seq['a']
        del e.seq['b']

        e.seq = {'a':'a'}
        del e.seq['a']

        class Example(ast.Node):
            seq = ast.dict(str, null=False)

        self.assertRaises(TypeError, Example)
        self.assertRaises(TypeError, Example, {'a':2})

        e = Example({'a':'a', 'b':'b'})

        self.assertRaises(TypeError, e.__setattr__, 'seq', None)
        self.assertRaises(TypeError, e.__setattr__, 'seq', {})

        e.seq = {'a':'a', 'b':'b', 'c':'c'}

        self.assertEqual(e.seq['c'], 'c')

        self.assertRaises(TypeError, e.__setattr__, 'seq', {'a': 'a',
                                                            'b': 3,
                                                            'c': 'c'})

        e.seq = {'a':'a'}
        self.assertRaises(TypeError, e.seq.pop, 'a')

        self.assertRaises(TypeError, e.seq.__delitem__, 0)

        e.seq[0] = 'd'

        self.assertRaises(TypeError, e.seq.__setitem__, 0, 2)

    def test_pattern(self):
        class Example(ast.Node):
            _debug = True
            seq = ast.seq(ast.re("[a-z]{2}"))

        e = Example(['ab','ba'])
        self.assertEqual(len(e.seq), 2)
        self.assertEqual(e.seq[0], 'ab')
        self.assertEqual(e.seq[1], 'ba')

        self.assertRaises(TypeError, Example, "0a")
    
    def test_pattern2(self):
        class Example(ast.Node):
            _debug = True
            seq = ast.seq((ast.re("[a-z]{2}"), ast.re("[1-9]{1}")))

        e = Example(['ab','ba'])
        self.assertEqual(len(e.seq), 2)
        self.assertEqual(e.seq[0], 'ab')
        self.assertEqual(e.seq[1], 'ba')

        self.assertRaises(TypeError, Example, "0a")
    
    def test_basic_inheritance(self):
        class Example(ast.Node):
            _debug = True
            field = ast.field(str, null=True)
      
        class Example4(ast.Node):
            field2 = ast.field(str)

        class Example2(Example, Example4):
            pass

        e = Example2(field="test", field2="dd")
        self.assertEqual(type(e), Example2)
        self.assertEqual(e.field, "test")

    def test_basic_twomodes(self):
        class Example(ast.Node):
            _debug = True
            field = ast.field(str, null=True)
      
        class Example2(ast.Node):
            _debug = False
            field = ast.field(str)

        class Example3(ast.Node):
            _debug = True
            field = ast.field(str)

        self.assertRaises(TypeError, Example, 2)
        self.assertEqual(Example2(2).field, 2)
        self.assertRaises(TypeError, Example3, 2)

        x = Example2()
        x._foo = 'x'
        self.assertEqual(x._foo, 'x')

    def test_basic_init_template(self):
        class Example(ast.Node):
            _debug = True
            key = ast.field(str, null=True)
            value = ast.field((str, int), null=True)

        e = Example(key='key', value='s')
        e._template = '<%(key)s %(value)s>'
        x = str(e)
        self.assertEqual(x, '<key s>')

    def test_basic_seq_template(self):

        class Literal(ast.Node):
            content = ast.field(str)
            _template = '%(content)s'
        
        class Example(ast.Node):
            _debug = True
            key = ast.field(Literal, null=True)
            value = ast.seq(Literal, null=True)

        e = Example(key=Literal('key'), value=[Literal('a'), Literal('b')])
        e._template = '<%(key)s [%(value)s]>'
        x = str(e)
        self.assertEqual(x, '<key [a, b]>')
    
    def test_basic_seq_custom_template(self):

        class Literal(ast.Node):
            content = ast.field(str)
            _template = '%(content)s'
        
        class Example(ast.Node):
            _debug = True
            key = ast.field(Literal, null=True)
            value = ast.seq(Literal, null=True)

        key = Literal('key')

        a = Literal('a')
        b = Literal('b')
        value = [a,b]

        e = Example(key=key, value=value)
        e._template = '< %(key)s   [ %(value)s ]>'
        e._template_value = ['', '  ,   ']
        x = str(e)
        self.assertEqual(x, '< key   [ a  ,   b ]>')

if __name__ == '__main__':
    unittest.main()


