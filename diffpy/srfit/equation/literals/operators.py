#!/usr/bin/env python
########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################
"""Operator classes. 

Operators are combined with other Literals to create an equation. Operators are
non-leaf nodes on a Literal tree. These trees can be evaluated by the Evaluator
visitor, or otherwise inspected. 

The Operator class contains all the information necessary to be identified and
evaluated by a Visitor. Thus, a single onOperator method exists in the Visitor
base class. Other Operators can be derived from Operator (see AdditionOperator),
but they all identify themselves with the Visitor.onOperator method.

"""


from .abcs import OperatorABC
from .literal import Literal

import numpy

class Operator(Literal, OperatorABC):
    """Class for holding a general operator.

    This holds a general operator and records its function, arguments, name and
    symbol.  The visitors should be able to process any Operator with this
    information alone.

    Attributes
    args    --  List of Literal arguments, set with 'addLiteral'
    name    --  A name for this operator. e.g. "add" or "sin"
    nin     --  Number of inputs (<1 means this is variable)
    nout    --  Number of outputs
    operation   --  Function that performs the operation. e.g. numpy.add or
    symbol  --  The symbolic representation. e.g. "+" or "sin"
                numpy.sin
    _value  --  The value of the Argument. Modified with 'setValue'.
    value   --  Property for 'getValue' and 'setValue'.

    """

    # Required attributes - used for type checking
    args = None
    nin = None
    nout = None
    operation = None
    symbol = None
    _value = None

    def __init__(self, name = None, symbol = None, operation = None, nin = 2,
            nout = 1):
        """Initialization."""
        Literal.__init__(self, name)
        self.symbol = symbol
        self.nin = nin
        self.nout = nout
        self.args = []
        self.operation = operation
        return

    def identify(self, visitor):
        """Identify self to a visitor."""
        return visitor.onOperator(self)

    def addLiteral(self, literal):
        """Add a literal to this operator.

        Note that order of operation matters. The first literal added is the
        leftmost argument. The last is the rightmost.

        Raises ValueError if the literal causes a self-reference.

        """
        # Make sure we don't have self-reference
        self._loopCheck(literal)
        self.args.append(literal)
        literal.addObserver(self._flush)
        self._flush(None)
        return

    def getValue(self):
        """Get or evaluate the value of the operator."""
        if self._value is not None:
            return self._value

        vals = [l.value for l in self.args]
        return self.operation(*vals)

    def _loopCheck(self, literal):
        """Check if a literal causes self-reference."""
        if literal is self:
            raise ValueError("'%s' causes self-reference"%literal)

        # Check to see if I am a dependency of the literal.
        if hasattr(literal, "args"):
            for l in literal.args:
                self._loopCheck(l)
        return

    def __str__(self):
        if self.name:
            return "Operator(" + self.name + ")"
        return self.__repr__()

    value = property(getValue)


# Some specified operators


class AdditionOperator(Operator):
    """Addition operator."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "add"
        self.symbol = "+"
        self.operation = numpy.add
        return

class SubtractionOperator(Operator):
    """Subtraction operator."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "subtract"
        self.symbol = "-"
        self.operation = numpy.subtract
        return

class MultiplicationOperator(Operator):
    """Multiplication operator."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "multiply"
        self.symbol = "*"
        self.operation = numpy.multiply
        return

class DivisionOperator(Operator):
    """Division operator."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "divide"
        self.symbol = "/"
        self.operation = numpy.divide
        return

class ExponentiationOperator(Operator):
    """Exponentiation operator."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "power"
        self.symbol = "**"
        self.operation = numpy.power
        return

class RemainderOperator(Operator):
    """Remainder operator."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "mod"
        self.symbol = "%"
        self.operation = numpy.mod
        return

class NegationOperator(Operator):
    """Negation operator."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "negative"
        self.symbol = "-"
        self.nin = 1
        self.operation = numpy.negative
        return

class ConvolutionOperator(Operator):
    """Scaled version of the numpy.convolve operator.

    This calls numpy.convolve, but divides by the sum of the second argument in
    hopes of preserving the scale of the first argument.
    numpy.conolve(v1, v2, mode = "same")/sum(v2)
    It then truncates to the length of the first array.

    """

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "convolve"
        self.symbol = "convolve"

        def conv(v1, v2):
            """numpy.conolve(v1, v2, mode = "same")/sum(v2)"""
            c = numpy.convolve(v1, v2, mode="same")/sum(v2)
            c.resize((len(v1),))
            return c

        self.operation = conv
        return


class SumOperator(Operator):
    """numpy.sum operator."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "sum"
        self.symbol = "sum"
        self.nin = 1
        self.nout = 1
        self.operation = numpy.sum
        return

class UFuncOperator(Operator):
    """A operator wrapper around a numpy ufunc.

    The name and symbol attributes are set equal to the ufunc.__name__
    attribute. nin and nout are also taken from the ufunc.
    
    """

    def __init__(self, op):
        """Initialization.

        Arguments
        op  --  A numpy ufunc

        """
        Operator.__init__(self)
        self.name = op.__name__
        self.symbol = op.__name__
        self.nin = op.nin
        self.nout = op.nout
        self.operation = op
        return

class ListOperator(Operator):
    """Operator that will take parameters and turn them into a list."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "list"
        self.symbol = "list"
        self.nin = -1

        def makeList(*args):
            return args

        self.operation = makeList
        return

class SetOperator(Operator):
    """Operator that will take parameters and turn them into a set."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "set"
        self.symbol = "set"
        self.nin = -1

        def makeSet(*args):
            return set(args)

        self.operation = makeSet
        return

class ArrayOperator(Operator):
    """Operator that will take parameters and turn them into an array."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "array"
        self.symbol = "array"
        self.nin = -1

        def makeArray(*args):
            return numpy.array(args)

        self.operation = makeArray
        return


class PolyvalOperator(Operator):
    """Operator for numpy polyval."""

    def __init__(self):
        """Initialization."""
        Operator.__init__(self)
        self.name = "polyval"
        self.symbol = "polyval"
        self.nin = 2
        self.operation = numpy.polyval
        return

# version
__id__ = "$Id$"

#
# End of file
