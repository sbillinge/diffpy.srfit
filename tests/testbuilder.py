#!/usr/bin/env python
"""Tests for refinableobj module."""

import diffpy.srfit.equation.builder as builder
import diffpy.srfit.equation.literals as literals

import unittest

import numpy

from utils import _makeArgs

class TestRegistration(unittest.TestCase):

    def testRegisterArg(self):

        factory = builder.EquationFactory()

        v1 = _makeArgs(1)[0]

        factory.registerArgument("v1", v1)

        eq = factory.makeEquation("v1")

        self.assertTrue(v1 is eq.args[0])
        self.assertEquals(1, len(eq.args))

        # Try to parse an equation with buildargs turned off
        self.assertRaises(ValueError, factory.makeEquation, "v1 + v2", False)

        # Make sure we can still use constants
        eq = factory.makeEquation("v1 + 2", False)
        self.assertTrue(v1 is eq.args[0])
        self.assertEquals(1, len(eq.args))
        return



class TestEquationParser(unittest.TestCase):

    def testParseEquation(self):

        from numpy import exp, sin, divide, sqrt, array_equal, e

        factory = builder.EquationFactory()

        # Scalar equation
        eq = factory.makeEquation("A*sin(0.5*x)+divide(B,C)")
        A = 1
        x = numpy.pi
        B = 4.0
        C = 2.0
        eq.A.setValue(A)
        eq.x.setValue(x)
        eq.B.setValue(B)
        eq.C.setValue(C)
        f = lambda A, x, B, C: A*sin(0.5*x)+divide(B,C)
        self.assertTrue(array_equal(eq(), f(A,x,B,C)))

        # Make sure that the arguments of eq are listed in the order in which
        # they appear in the equations.
        self.assertEquals(eq.args, [eq.A, eq.x, eq.B, eq.C])

        # Vector equation
        eq = factory.makeEquation("sqrt(e**(-0.5*(x/sigma)**2))")
        x = numpy.arange(0, 1, 0.05)
        sigma = 0.1
        eq.x.setValue(x)
        eq.sigma.setValue(sigma)
        f = lambda x, sigma : sqrt(e**(-0.5*(x/sigma)**2))
        self.assertTrue(array_equal(eq(), f(x,sigma)))

        self.assertEquals(eq.args, [eq.x, eq.sigma])

        # Equation with constants
        factory.registerConstant("x", x)
        eq = factory.makeEquation("sqrt(e**(-0.5*(x/sigma)**2))")
        self.assertTrue("sigma" in eq.argdict)
        self.assertTrue("x" not in eq.argdict)
        self.assertTrue(array_equal(eq(sigma=sigma), f(x,sigma)))

        self.assertEquals(eq.args, [eq.sigma])

        # Equation with user-defined functions
        factory.registerFunction("myfunc", eq, 1)
        eq2 = factory.makeEquation("c*myfunc(sigma)")
        self.assertTrue(array_equal(eq2(c=2, sigma=sigma), 2*f(x,sigma)))
        self.assertTrue("sigma" in eq2.argdict)
        self.assertTrue("c" in eq2.argdict)
        self.assertEquals(eq2.args, [eq2.c, eq2.sigma])

        # Equation with partition
        return

    def testBuildEquation(self):

        from numpy import array_equal

        # simple equation
        sin = builder.getBuilder("sin")
        a = builder.ArgumentBuilder(name="a", value = 1)
        A = builder.ArgumentBuilder(name="A", value = 2)
        x = numpy.arange(0, numpy.pi, 0.1)

        beq = A*sin(a*x)
        eq = beq.getEquation()

        self.assertTrue("a" in eq.argdict)
        self.assertTrue("A" in eq.argdict)
        self.assertTrue(array_equal(eq(), 2*numpy.sin(x)))

        self.assertEquals(eq.args, [eq.A, eq.a])

        # Check the number of arguments
        self.assertRaises(ValueError, sin)

        # custom function
        def _f(a, b):
            return (a-b)*1.0/(a+b)

        f = builder.wrapFunction("f", _f, 2, 1)
        a = builder.ArgumentBuilder(name="a", value = 2)
        b = builder.ArgumentBuilder(name="b", value = 1)

        beq = sin(f(a,b))
        eq = beq.getEquation()
        self.assertEqual(eq(), numpy.sin(_f(2, 1)))

        # complex function
        sqrt = builder.getBuilder("sqrt")
        e = numpy.e
        _x = numpy.arange(0, 1, 0.05)
        x = builder.ArgumentBuilder(name="x", value = _x, const = True)
        sigma = builder.ArgumentBuilder(name="sigma", value = 0.1)
        beq = sqrt(e**(-0.5*(x/sigma)**2))
        eq = beq.getEquation()
        f = lambda x, sigma : sqrt(e**(-0.5*(x/sigma)**2))
        self.assertTrue(array_equal(eq(), numpy.sqrt(e**(-0.5*(_x/0.1)**2))))

        # Equation with Equation
        A = builder.ArgumentBuilder(name="A", value = 2)
        B = builder.ArgumentBuilder(name="B", value = 4)
        beq = A + B
        eq = beq.getEquation()
        E = builder.wrapEquation("eq", eq)
        eq2 = (2*E).getEquation()
        # Make sure these evaulate to the same thing
        self.assertEquals(eq.args, [A.literal, B.literal])
        self.assertEquals(2*eq(), eq2())
        # Pass new arguments to the equation
        C = builder.ArgumentBuilder(name="C", value = 5)
        D = builder.ArgumentBuilder(name="D", value = 6)
        eq3 = (E(C, D)+1).getEquation()
        self.assertEquals(12, eq3())
        # Pass old and new arguments to the equation
        # If things work right, A has been given the value of C in the last
        # evaluation (5)
        eq4 = (3*E(A, D)-1).getEquation()
        self.assertEquals(32, eq4())
        # Try to pass the wrong number of arguments
        self.assertRaises(ValueError, E, A)
        self.assertRaises(ValueError, E, A, B, C)
        
        return


if __name__ == "__main__":

    unittest.main()

