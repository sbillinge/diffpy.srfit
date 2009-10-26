#!/usr/bin/env python
"""Tests for refinableobj module."""

import unittest

from diffpy.srfit.fitbase.parameter import *

class TestParameter(unittest.TestCase):

    def testSetValue(self):
        """Test initialization."""
        l = Parameter("l")

        l.setValue(3.14)
        self.assertAlmostEqual(3.14, l.getValue())

        # Try array
        import numpy
        x = numpy.arange(0, 10, 0.1)
        l.setValue(x)
        self.assertTrue( l.getValue() is x )
        self.assertTrue( l.value is x )

        # Change the array
        y = numpy.arange(0, 10, 0.5)
        l.value = y
        self.assertTrue( l.getValue() is y )
        self.assertTrue( l.value is y )

        # Back to scalar
        l.setValue(1.01)
        self.assertAlmostEqual(1.01, l.getValue())
        self.assertAlmostEqual(1.01, l.value)
        return

    def testConstraint(self):
        """Test a constrained parameter."""
        l = Parameter("l")
        l.setValue(3.14)

        from diffpy.srfit.equation.equationmod import Equation
        l0 = Parameter("zero", 0)
        constraint = Equation(root = l0)

        self.assertAlmostEqual(3.14, l.getValue())

        l.constrain(constraint)
        self.assertTrue(l._value is None)
        self.assertAlmostEqual(0, l.getValue())

        l.unconstrain()
        self.assertAlmostEqual(0, l.getValue())

        # Constrain in a chain
        l.value = 3.14
        l2 = Parameter("l2", 1.23)
        self.assertAlmostEquals(1.23, l2.value)
        constraint2 = Equation(root = l)
        l2.constrain(constraint2)
        self.assertAlmostEquals(3.14, l2.value)
        l.constrain(constraint)
        self.assertAlmostEquals(0, l2.value)
        self.assertAlmostEquals(0, l.value)

        return

class TestParameterProxy(unittest.TestCase):

    def testProxy(self):
        """Test the ParameterProxy class."""
        l = Parameter("l", 3.14)

        # Try Accessor adaptation
        la = ParameterProxy("l2", l)

        self.assertEqual("l2", la.name)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the parameter
        l.value = 2.3
        self.assertEqual(l.getValue(), la.getValue())

        # Change the proxy
        la.value = 3.2
        self.assertEqual(l.getValue(), la.getValue())

        return

    def testConstraint(self):
        """Test a constrained parameter."""
        l = Parameter("l", 3.14)
        la = ParameterProxy("l2", l)

        from diffpy.srfit.equation.equationmod import Equation
        l0 = Parameter("zero", 0)
        constraint = Equation(root = l0)

        self.assertAlmostEqual(3.14, l.value)
        self.assertAlmostEqual(3.14, la.getValue())

        l.constrain(constraint)
        self.assertAlmostEqual(0, l.getValue())
        self.assertAlmostEqual(0, la.getValue())

        la.unconstrain()
        self.assertAlmostEqual(0, l.getValue())
        self.assertAlmostEqual(0, la.getValue())
        return

class TestParameterWrapper(unittest.TestCase):

    def testWrapper(self):
        """Test the adapter.

        This adapts a Parameter to the Parameter interface. :)
        """
        l = Parameter("l", 3.14)

        # Try Accessor adaptation
        la = ParameterWrapper("l", l, getter = Parameter.getValue, setter =
                Parameter.setValue)

        self.assertEqual(l.name, la.name)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the parameter
        l.setValue(2.3)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the adapter
        la.setValue(3.2)
        self.assertEqual(l.getValue(), la.getValue())

        # Try Attribute adaptation
        la = ParameterWrapper("l", l, attr = "value")

        self.assertEqual(l.name, la.name)
        self.assertEqual("value", la.attr)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the parameter
        l.setValue(2.3)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the adapter
        la.setValue(3.2)
        self.assertEqual(l.getValue(), la.getValue())

        return

    def testConstraint(self):
        """Test a constrained parameter."""
        l = Parameter("l", 3.14)
        la = ParameterWrapper("l", l, getter = Parameter.getValue, setter =
                Parameter.setValue)

        from diffpy.srfit.equation.equationmod import Equation
        l0 = Parameter("zero", 0)
        constraint = Equation(root = l0)

        self.assertAlmostEqual(3.14, l.getValue())
        self.assertAlmostEqual(3.14, la.getValue())

        l.constrain(constraint)
        self.assertAlmostEqual(0, l.getValue())
        self.assertAlmostEqual(0, la.getValue())

        la.unconstrain()
        self.assertAlmostEqual(0, l.getValue())
        self.assertAlmostEqual(0, la.getValue())
        return

if __name__ == "__main__":

    unittest.main()

