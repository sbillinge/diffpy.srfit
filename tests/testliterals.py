#!/usr/bin/env python
"""Tests for refinableobj module."""

import unittest

import numpy

import diffpy.srfit.equation.literals as literals


class TestArgument(unittest.TestCase):

    def testInit(self):
        """Test that everthing initializes as expected."""
        a = literals.Argument()
        self.assertEqual(None, a._value)
        self.assertTrue(False is a.const)
        self.assertTrue(None is a.name)
        return

    def testValue(self):
        """Test value setting."""

        a = literals.Argument()

        # Test error when there is no value
        self.assertRaises(ValueError, a.getValue)

        # Test setting value
        a.setValue(3.14)
        self.assertAlmostEqual(a._value, 3.14)

        a.setValue(3.14)
        self.assertAlmostEqual(a.value, 3.14)
        return

class TestOperator(unittest.TestCase):

    def testInit(self):
        """Test that everthing initializes as expected."""
        op = literals.Operator(symbol = "+", operation = numpy.add, nin = 2)

        self.assertEqual("+", op.symbol)
        self.assertEqual(numpy.add, op.operation)
        self.assertEqual(2, op.nin)
        self.assertEqual(1, op.nout)
        self.assertEqual(None, op._value)
        self.assertEqual([], op.args)
        return

    def testValue(self):
        """Test value."""
        # Test addition and operations
        op = literals.Operator(symbol = "+", operation = numpy.add, nin = 2)
        a = literals.Argument(value = 0)
        b = literals.Argument(value = 0)

        op.addLiteral(a)
        op.addLiteral(b)

        self.assertAlmostEquals(0, op.value)

        # Test update from the nodes
        a.setValue(4)
        self.assertTrue(op._value is None)
        self.assertAlmostEqual(4, op.value)

        b.value = 2
        self.assertTrue(op._value is None)
        self.assertAlmostEqual(6, op.value)

        return

    def testAddLiteral(self):
        """Test adding a literal to an operator node."""
        op = literals.Operator(name = "add", symbol = "+", operation =
                numpy.add, nin = 2, nout = 1)

        self.assertRaises(ValueError, op.getValue)
        op._value = 1
        self.assertEqual(op.getValue(), 1)

        # Test addition and operations
        a = literals.Argument(name = "a", value = 0)
        b = literals.Argument(name = "b", value = 0)

        op.addLiteral(a)
        self.assertRaises(ValueError, op.getValue)

        op.addLiteral(b)
        self.assertAlmostEqual(op.getValue(), 0)

        a.setValue(1)
        b.setValue(2)
        self.assertAlmostEqual(op.getValue(), 3)

        a.setValue(None)
        self.assertRaises(ValueError, op.getValue)

        # Test for self-references

        # Try to add self
        op = literals.Operator(name = "add", symbol = "+", operation =
                numpy.add, nin = 2, nout = 1)
        op.addLiteral(a)
        self.assertRaises(ValueError, op.addLiteral, op)

        # Try to add argument that contains self
        op2 = literals.Operator(name = "sub", symbol = "-", operation =
                numpy.subtract, nin = 2, nout = 1)
        op2.addLiteral(op)
        self.assertRaises(ValueError, op.addLiteral, op2)

        return



if __name__ == "__main__":

    unittest.main()

