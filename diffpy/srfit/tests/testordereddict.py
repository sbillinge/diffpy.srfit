#!/usr/bin/env python
##############################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 The Trustees of Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE_DANSE.txt for license information.
#
##############################################################################

from random import shuffle
import copy
import inspect
import pickle
import unittest


from diffpy.srfit.util.ordereddict import OrderedDict


class TestOrderedDict(unittest.TestCase):

    def test_init(self):
        self.assertRaises(TypeError, OrderedDict, ([('a', 1), ('b', 2)], None))
                # too many args
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        self.assertEqual(sorted(OrderedDict(dict(pairs)).items()), pairs)           # dict input
        self.assertEqual(sorted(OrderedDict(**dict(pairs)).items()), pairs)         # kwds input
        self.assertEqual(list(OrderedDict(pairs).items()), pairs)                   # pairs input
        self.assertEqual(list(OrderedDict([('a', 1), ('b', 2), ('c', 9), ('d', 4)],
                                          c=3, e=5).items()), pairs)                # mixed input

        # make sure no positional args conflict with possible kwdargs
        odargs = inspect.getargspec(OrderedDict.__dict__['__init__'])[0]
        self.assertTrue(odargs == [] or odargs == ['self'])

        # Make sure that direct calls to __init__ do not clear previous contents
        d = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 44), ('e', 55)])
        d.__init__([('e', 5), ('f', 6)], g=7, d=4)
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)])

    def test_update(self):
        self.assertRaises(TypeError, OrderedDict().update, [('a', 1), ('b',
            2)], None)                        # too many args
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        od = OrderedDict()
        od.update(dict(pairs))
        self.assertEqual(sorted(od.items()), pairs)                                 # dict input
        od = OrderedDict()
        od.update(**dict(pairs))
        self.assertEqual(sorted(od.items()), pairs)                                 # kwds input
        od = OrderedDict()
        od.update(pairs)
        self.assertEqual(list(od.items()), pairs)                                   # pairs input
        od = OrderedDict()
        od.update([('a', 1), ('b', 2), ('c', 9), ('d', 4)], c=3, e=5)
        self.assertEqual(list(od.items()), pairs)                                   # mixed input

        # Make sure that direct calls to update do not clear previous contents
        # add that updates items are not moved to the end
        d = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 44), ('e', 55)])
        d.update([('e', 5), ('f', 6)], g=7, d=4)
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)])

    def test_clear(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(len(od), len(pairs))
        od.clear()
        self.assertEqual(len(od), 0)

    def test_delitem(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        del od['a']
        self.assert_('a' not in od)
        self.assertRaises(KeyError, od.__delitem__, 'a')
        self.assertEqual(list(od.items()), pairs[:2] + pairs[3:])

    def test_setitem(self):
        od = OrderedDict([('d', 1), ('b', 2), ('c', 3), ('a', 4), ('e', 5)])
        od['c'] = 10           # existing element
        od['f'] = 20           # new element
        self.assertEqual(list(od.items()),
                         [('d', 1), ('b', 2), ('c', 10), ('a', 4), ('e', 5), ('f', 20)])

    def test_iterators(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(list(od), [t[0] for t in pairs])
        self.assertEqual(list(od.keys()), [t[0] for t in pairs])
        self.assertEqual(list(od.values()), [t[1] for t in pairs])
        self.assertEqual(list(od.items()), pairs)
        self.assertEqual(list(reversed(od)),
                         [t[0] for t in reversed(pairs)])

    def test_popitem(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        while pairs:
            self.assertEqual(od.popitem(), pairs.pop())
        self.assertRaises(KeyError, od.popitem)
        self.assertEqual(len(od), 0)

    def test_pop(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        shuffle(pairs)
        while pairs:
            k, v = pairs.pop()
            self.assertEqual(od.pop(k), v)
        self.assertRaises(KeyError, od.pop, 'xyz')
        self.assertEqual(len(od), 0)
        self.assertEqual(od.pop(k, 12345), 12345)

    def test_equality(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od1 = OrderedDict(pairs)
        od2 = OrderedDict(pairs)
        self.assertEqual(od1, od2)          # same order implies equality
        pairs = pairs[2:] + pairs[:2]
        od2 = OrderedDict(pairs)
        self.assertNotEqual(od1, od2)       # different order implies inequality
        # comparison to regular dict is not order sensitive
        self.assertEqual(od1, dict(od2))
        self.assertEqual(dict(od2), od1)
        # different length implied inequality
        self.assertNotEqual(od1, OrderedDict(pairs[:-1]))

    def test_copying(self):
        # Check that ordered dicts are copyable, deepcopyable, picklable,
        # and have a repr/eval round-trip
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        update_test = OrderedDict()
        update_test.update(od)
        for i, dup in enumerate([
                    od.copy(),
                    copy.copy(od),
                    copy.deepcopy(od),
                    pickle.loads(pickle.dumps(od, 0)),
                    pickle.loads(pickle.dumps(od, 1)),
                    pickle.loads(pickle.dumps(od, 2)),
                    pickle.loads(pickle.dumps(od, -1)),
                    eval(repr(od)),
                    update_test,
                    OrderedDict(od),
                    ]):
            self.assert_(dup is not od)
            self.assertEquals(dup, od)
            self.assertEquals(list(dup.items()), list(od.items()))
            self.assertEquals(len(dup), len(od))
            self.assertEquals(type(dup), type(od))

    def test_repr(self):
        od = OrderedDict([('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)])
        self.assertEqual(repr(od),
            "OrderedDict([('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)])")
        self.assertEqual(eval(repr(od)), od)
        self.assertEqual(repr(OrderedDict()), "OrderedDict()")

    def test_setdefault(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        pair_order = list(od.items())
        self.assertEqual(od.setdefault('a', 10), 3)
        # make sure order didn't change
        self.assertEqual(list(od.items()), pair_order)
        self.assertEqual(od.setdefault('x', 10), 10)
        # make sure 'x' is added to the end
        self.assertEqual(list(od.items())[-1], ('x', 10))

    def test_reinsert(self):
        # Given insert a, insert b, delete a, re-insert a,
        # verify that a is now later than b.
        od = OrderedDict()
        od['a'] = 1
        od['b'] = 2
        del od['a']
        od['a'] = 1
        self.assertEqual(list(od.items()), [('b', 2), ('a', 1)])


if __name__ == "__main__":
    unittest.main()
