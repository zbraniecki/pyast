import unittest
import sys
sys.path.insert(0, './')

from pyast.typeddict import TypedDict


class BaseTypedDictTestCase(unittest.TestCase):
    def test_basic(self):
        a = TypedDict(str, null=True)

        a['foo'] = "foo"
        self.assertRaises(TypeError, a.__setitem__, 'foo', 2)

        self.assertEquals(a['foo'], "foo")

        a['x'] = 'ble'
        self.assertEquals(len(a), 2)
        self.assertEquals(a['x'], "ble")

    def test_not_null(self):
        self.assertRaises(TypeError, TypedDict, types=(str,))

        a = TypedDict(str,
                      init={'foo': 'Hello'})
        self.assertEquals(len(a), 1)
        self.assertEquals(a['foo'], "Hello")

        self.assertRaises(TypeError, a.__delitem__, 0)

        a['x'] = 'ble'
        del a['foo']
        self.assertEquals(len(a), 1)

        self.assertRaises(TypeError, a.pop) 


if __name__ == '__main__':
    unittest.main()



