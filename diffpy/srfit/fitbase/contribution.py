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
"""Contribution class. 

Contributions organize an Equation and Calculator that calculate the signal,
and a Profile that holds the signal.
"""

from numpy import concatenate, sqrt, inf, dot

from diffpy.srfit.equation import Equation

from .parameter import Parameter
from .modelorganizer import ModelOrganizer, equationFromString


class Contribution(ModelOrganizer):
    """Contribution class.

    Contributions organize an Equation that calculates the signal, and a
    Profile that holds the signal. Contraints and Restraints can be created as
    part of a Contribution.

    Attributes
    clicker         --  A Clicker instance for recording changes in contained
                        Parameters and Contributions.
    name            --  A name for this Contribution.
    _aliasmap       --  A map from Parameters to their aliases.
    _calcname       --  A name for the Calculator.
    _calculator     --  A Calculator instance for generating a signal.
                        Contributions can share a Calculator instance.
    _constraints    --  A dictionary of Constraints, indexed by the constrained
                        Parameter. Constraints can be added using the
                        'constrain' method.
    _profile        --  A Profile that holds the measured (and calcuated)
                        signal.
    _eq             --  An Equation instance that generates a modified profile
                        with the Calculator.
    _eqfactory      --  A diffpy.srfit.equation.builder.EquationFactory
                        instance that is used to create constraints and
                        restraints from strings.
    _fixed          --  A list of Parameters that are fixed, but still managed
                        by the FitModel.
    _organizers     --  A reference to the Calcualtor's _organizers attribute.
    _orgdict        --  A reference to the Calculator's _orgdict attribute.
    _parameters     --  A reference to the Calculator's _parameters attribute.
    _restraints     --  A set of Restraints. Restraints can be added using the
                        'restrain' method.
    _weights        --  The weighing factor for each contribution. This value
                        is multiplied by the residual of the contribution when
                        determining the overall residual.

    """

    def __init__(self, name):
        """Initialization."""
        ModelOrganizer.__init__(self, name)
        self._eq = None
        self._profile = None
        self._calculator = None
        self._calcname = None
        return

    def setProfile(self, profile):
        """Assign the profile for this contribution.
        
        profile --  A Profile that specifies the calculation points and which
                    will store the calculated signal.

        """
        self._profile = profile
        return

    def setCalculator(self, calc, name):
        """Set the Calculator to be used by this Contribution.

        The Calculator is given a name so that it can be used as part of the
        equation that is used to generate the signal.

        calc    --  A Calculator instance
        name    --  A name for the calculator

        """
        self._calculator = calc
        self._calcname = name

        # Let the ModelOrganizer structure know of the calculator
        self._addOrganizer(calc)

        # Register the calculator with the equation factory
        self._eqfactory.registerGenerator(name, calc)

        # Create the default equation
        self._eq = self._eqfactory.makeEquation(name)

        return

    def setEquation(self, eqstr, ns = {}):
        """Set the refinement equation for the Contribution.

        eqstr   --  A string representation of the equation. The name of the
                    Calculator can be used in the equation. Any variables that
                    appear within eqstr will be added to the Contribution, and
                    will be accessible as attributes.
        ns      --  A dictionary of Parameters, indexed by name, that are used
                    in the eqstr, but not part of the Calculator (default
                    {}).

        Raises AttributeError if the Calculator is not yet defined.
        Raises ValueError if ns uses a name that is already used for a
        Parameter.
        Raises ValueError if eqstr depends on a Parameter that is not part of
        the Calculator and that is not defined in ns.
        """
        if self._calculator is None:
            raise AttributeError("Define the calculator first")

        self._eq = equationFromString(eqstr, self._eqfactory, ns)

        return

    def residual(self):
        """Calculate the residual for this contribution.

        It is assumed that all parameters have been assigned their most current
        values by the FitModel.

        The residual is by default an array chiv:
        chiv = (eq() - self._profile.y) / self._profile.dy
        
        """

        # Make sure that the calculator knows about the profile associated with
        # this contribution since multiple contributions may be using the same
        # calculator.
        self._calculator.setProfile(self._profile)

        chiv = (self._eq() - self._profile.y) / self._profile.dy
        return chiv


# version
__id__ = "$Id$"

#
# End of file
