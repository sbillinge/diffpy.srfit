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
"""Example of fitting the Debye model to experimental Debye-Waller factors.

This is an extension of example in debyemodel.py. Here we fit the low and high
temperature parts of the data simultaneously using the same debye temperature,
but different offsets.

Once you understand this, move on to the intensitycalculator.py example.
"""
import numpy

from diffpy.srfit.fitbase import FitModel

from debyemodel import makeModel, scipyOptimize, parkOptimize

def makeModelII():
    """Make the model for our problem.

    We will make two models using the makeModel function from debyemodel.py. We
    will extract the contribution from the second model and use it in the
    first and fit both contributions simultaneously over different fit ranges,
    with the same Debye temperature.

    """

    # We'll throw these away. We just want the contributions that are
    # configured within the models.
    m1 = makeModel()
    m2 = makeModel()
    lowT = m1.pb
    highT = m2.pb
    # Let's rename the contributions
    lowT.name = "lowT"
    highT.name = "highT"

    # Now create a fresh model to work with
    model = FitModel()
    model.addContribution(lowT)
    model.addContribution(highT)

    # Let's change the fit ranges on our contributions
    lowT.profile.setCalculationRange(0, 150)
    highT.profile.setCalculationRange(400, 500)

    # Now the constraints. We want to let the offset from each model vary
    # freely while keeping the Debye temperatures the same.
    model.addVar(model.lowT.offset, name = "lowToffset")
    model.addVar(model.highT.offset, name = "highToffset")
    model.newVar("tvar", 300)
    model.constrain(model.lowT.thetaD, "abs(tvar)")
    model.constrain(model.highT.thetaD, "abs(tvar)")

    return model

def displayResults(model):
    """Display the results contained within a refined FitModel."""

    # For the basic info about the fit, we can use the FitModel directly
    chiv = model.residual()

    print "Chi^2 = ", numpy.dot(chiv, chiv)
    # Get the refined variable values, noting that we didn't refine thetaD
    # directly. If we want uncertainties, we have to go to the optimizer
    # directly.
    lowToffset, highToffset, tvar = model.getValues()

    print "tvar =", tvar
    print "lowToffset =", lowToffset
    print "highToffset =", highToffset
    
    # Plot this.
    # We want to extend the fitting range to its full extent so we can get a
    # nice full plot. We need to call the equation for each contribution to
    # update the range of the calculated profile.
    model.lowT.profile.setCalculationRange()
    model.highT.profile.setCalculationRange()
    T = model.lowT.profile.x
    U = model.lowT.profile.y
    lowU = model.lowT.evaluateEquation("eq()")
    highU = model.highT.evaluateEquation("eq()")

    import pylab
    pylab.plot(T,U,'o',label="Pb $U_{iso}$ Data")
    lbl1 = "$T_d$=%3.1f K, lowToff=%1.5f $\AA^2$"% (abs(tvar),lowToffset)
    lbl2 = "$T_d$=%3.1f K, highToff=%1.5f $\AA^2$"% (abs(tvar),highToffset)
    pylab.plot(T,lowU,label=lbl1)
    pylab.plot(T,highU,label=lbl2)
    pylab.xlabel("T (K)")
    pylab.ylabel("$U_{iso} (\AA^2)$")
    pylab.legend(loc = (0.0,0.8))

    pylab.show()
    return

if __name__ == "__main__":

    model = makeModelII()
    scipyOptimize(model)
    displayResults(model)

    model = makeModelII()
    parkOptimize(model)
    displayResults(model)
    print \
"""\nNote that the solutions are equivalent (to several digits). We cannot assess
the parameter uncertainty without uncertainties on the data points.\
"""


# End of file