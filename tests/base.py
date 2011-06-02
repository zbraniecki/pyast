import unittest
import sys
sys.path.append('./lib')

import silme.format.l20n.ast.base as ast

class BaseASTTestCase(unittest.TestCase):
    def setUp(self):
        ast.DEBUG = True

    def test_basic_init(self):
        class Example(ast.Node):
            field = ast.field(str, null=True)
            seq = ast.seq((str, int), null=True)
        
        e = Example()
        self.assertIsInstance(e, Example)
        self.assertEqual(e.field, None)
        self.assertEqual(len(e.seq), 0)

        e = Example(field="foo")
        self.assertIsInstance(e, Example)
        self.assertEqual(e.field, "foo")
        self.assertEqual(len(e.seq), 0)

        self.assertRaises(TypeError, Example, {'field':2})

        e = Example(seq=('a', 2))
        self.assertIsInstance(e, Example)
        self.assertEqual(e.field, None)
        self.assertEqual(len(e.seq), 2)
        self.assertEqual(e.seq[0], 'a')
        self.assertEqual(e.seq[1], 2)

        e = Example(seq=('a', 2), field="foo")
        e2 = Example(field="foo", seq=('a', 2))
        self.assertIsInstance(e, Example)
        self.assertEqual(len(e.seq), len(e2.seq))
        self.assertEqual(e.seq[0], e2.seq[0])
        self.assertEqual(e.seq[1], e2.seq[1])
        self.assertEqual(e.field, e2.field)

    def test_not_null(self):
        class Example(ast.Node):
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

if __name__ == '__main__':
    unittest.main()

