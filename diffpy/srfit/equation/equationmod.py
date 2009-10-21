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
"""The Equation class for holding and evaluating an equation.

Equation is a functor that holds a Literal tree that defines an equation. It's
__call__ method evaluates the equation at the most recent value of its
Arguments. The non-constant arguments are accessible as attributes of the
Equation instance and can be passed as arguments to __call__.

Example
> # make a Literal tree. Here's a simple one
> add = AdditionOperator()
> a = Argument(name="a") # Don't forget to name these!
> b = Argument(name="b")
> add.addLiteral(a)
> add.addLiteral(b)
> # make an Equation instance and pass the root
> eq = Equation(root = add)
> eq(a=3, b=4) # returns 7
> eq(a=2) # remembers b=4, returns 6
> eq.a.setValue(-3)
> eq.b.setValue(3)
> eq() # uses last assignment of a and b, returns 0

See the class documentation for more information.

"""

from .visitors import validate, findArgs, swap

from diffpy.srfit.util.ordereddict import OrderedDict

class Equation(object):
    """Class for holding and evaluating a Literal tree.

    Instances have attributes that are the non-const Arguments of the tree
    (accessed by name) and a __call__ method that evaluates the tree.  It is
    assumed, but not enforced that Arguments have unique names.  If this is not
    the case, then one should keep its own list of Arguments.

    The tree is scanned for errors when it is added. Thus, the tree should be
    complete before putting it inside an Equation.

    Attributes
    root    --  The root Literal of the equation tree
    argdict --  An OrderedDict of Arguments from the root.
    args    --  Property that gets the values of argdict.

    """

    def __init__(self, root=None):
        """Initialize.

        root    --  The root node of the Literal tree (default None). If root
                    is not passed here, you must call the 'setRoot' method to
                    set or change the root node.

        """
        # Set required Operator data
        self.root = None
        self.argdict = OrderedDict()
        if root is not None:
            self.setRoot(root)
        return

    def _getArgs(self):
        return self.argdict.values()

    args = property(_getArgs)

    def __getattr__(self, name):
        """Gives access to the Arguments as attributes."""
        arg = self.argdict.get(name)
        if arg is None:
            raise AttributeError("No argument named '%s' here"%name)
        return arg

    def setRoot(self, root):
        """Set the root of the Literal tree.

        Raises:
        ValueError if errors are found in the Literal tree.

        """

        # Start by validating
        validate(root)
        self.root = root

        # Get the args
        args = findArgs(root, getconsts=False)
        self.argdict = OrderedDict( [(arg.name, arg) for arg in args] )
        
        return

    def __call__(self, *args, **kw):
        """Call the equation.
        
        New Argument values are acceped as arguments or keyword assignments (or
        both).  The order of accepted arguments is given by the args
        attribute.  The Equation will remember values set in this way.

        Raises
        ValueError when a passed argument cannot be found

        """
        # Process args
        for idx, val in enumerate(args):
            if idx > len(self.argdict):
                raise ValueError("Too many arguments")
            arg = self.args[idx]
            arg.setValue(val)

        # Process kw
        for name, val in kw.items():
            arg = self.argdict.get(name)
            if arg is None:
                raise ValueError("No argument named '%s' here"%name)
            arg.setValue(val)

        return self.root.getValue()
        
    def swap(self, oldlit, newlit):
        """Swap a literal in the equation for another."""
        newroot = swap(self.root, oldlit, newlit)
        self.setRoot(newroot)
        return

# version
__id__ = "$Id$"

#
# End of file
