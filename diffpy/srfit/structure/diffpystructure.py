#!/usr/bin/env python
########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2009 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################
"""Wrappers for interfacing a diffpy.Structure.Structure with SrFit.

A diffpy.Structure.Structure object is meant to be passed to a StrucureParSet
object from this module, which can then be used as a ParameterSet. Any change
to the lattice or existing atoms will be registered with the Structure. Changes
in the number of atoms will not be recognized. Thus, the
diffpy.Structure.Structure object should be fully configured before passing it
to Structure.

StructureParSet --  Adapter for diffpy.Structure.Structure
LatticeParSet   --  Adapter for diffpy.Structure.Lattice
AtomParSet      --  Adapter for diffpy.Structure.Atom

"""

__all__ = ["AtomParSet", "LatticeParSet", "StructureParSet"]

from diffpy.srfit.fitbase.parameter import Parameter, ParameterProxy
from diffpy.srfit.fitbase.parameter import ParameterAdapter
from diffpy.srfit.fitbase.parameterset import ParameterSet
from diffpy.srfit.structure.basestructure import BaseStructure

# Accessor for xyz of atoms
def _xyzgetter(i):

    def f(atom):
        return atom.xyz[i]

    return f

def _xyzsetter(i):

    def f(atom, value):
        atom.xyz[i] = value
        return

    return f

class AtomParSet(ParameterSet):
    """A wrapper for diffpy.Structure.Atom.

    This class derives from diffpy.srfit.fitbase.parameterset.ParameterSet. See
    this class for base attributes.

    Attributes:
    atom        --  The diffpy.Structure.Atom this is adapting
    element     --  The element name (property).

    Managed Parameters:
    x (y, z)    --  Atom position in crystal coordinates (ParameterAdapter)
    occupancy   --  Occupancy of the atom on its crystal location
                    (ParameterAdapter)
    occ         --  Proxy for occupancy (ParameterProxy).
    U11, U22, U33, U12, U21, U23, U32, U13, U31
                --  Anisotropic displacement factor for atom (ParameterAdapter
                    or ParameterProxy). Note that the Uij and Uji parameters
                    are the same.
    Uiso        --  Isotropic ADP (ParameterAdapter).
    B11, B22, B33, B12, B21, B23, B32, B13, B31
                --  Anisotropic displacement factor for atom (ParameterAdapter
                    or ParameterProxy). Note that the Bij and Bji parameters
                    are the same. (Bij = 8*pi**2*Uij)
    Biso        --  Isotropic ADP (ParameterAdapter).
    
    """

    def __init__(self, atom, name):
        """Initialize

        atom    --  A diffpy.Structure.Atom instance

        """
        ParameterSet.__init__(self, name)
        self.atom = atom
        a = atom
        # x, y, z, occupancy
        self.addParameter(ParameterAdapter("x", a, _xyzgetter(0),
            _xyzsetter(0)))
        self.addParameter(ParameterAdapter("y", a, _xyzgetter(1),
            _xyzsetter(1)))
        self.addParameter(ParameterAdapter("z", a, _xyzgetter(2),
            _xyzsetter(2)))
        occupancy = ParameterAdapter("occupancy", a, attr = "occupancy")
        self.addParameter(occupancy)
        self.addParameter(ParameterProxy("occ", occupancy))
        # U
        self.addParameter(ParameterAdapter("U11", a, attr = "U11"))
        self.addParameter(ParameterAdapter("U22", a, attr = "U22"))
        self.addParameter(ParameterAdapter("U33", a, attr = "U33"))
        U12 = ParameterAdapter("U12", a, attr = "U12")
        U21 = ParameterProxy("U21", U12)
        U13 = ParameterAdapter("U13", a, attr = "U13")
        U31 = ParameterProxy("U31", U13)
        U23 = ParameterAdapter("U23", a, attr = "U23")
        U32 = ParameterProxy("U32", U23)
        self.addParameter(U12)
        self.addParameter(U21)
        self.addParameter(U13)
        self.addParameter(U31)
        self.addParameter(U23)
        self.addParameter(U32)
        self.addParameter(ParameterAdapter("Uiso", a, attr = "Uisoequiv"))
        # B
        self.addParameter(ParameterAdapter("B11", a, attr = "B11"))
        self.addParameter(ParameterAdapter("B22", a, attr = "B22"))
        self.addParameter(ParameterAdapter("B33", a, attr = "B33"))
        B12 = ParameterAdapter("B12", a, attr = "B12")
        B21 = ParameterProxy("B21", B12)
        B13 = ParameterAdapter("B13", a, attr = "B13")
        B31 = ParameterProxy("B31", B13)
        B23 = ParameterAdapter("B23", a, attr = "B23")
        B32 = ParameterProxy("B32", B23)
        self.addParameter(B12)
        self.addParameter(B21)
        self.addParameter(B13)
        self.addParameter(B31)
        self.addParameter(B23)
        self.addParameter(B32)
        self.addParameter(ParameterAdapter("Biso", a, attr = "Bisoequiv"))

        # Other setup
        self.__repr__ = a.__repr__
        return

    def _getElem(self):
        return self.atom.element

    def _setElem(self, el):
        self.atom.element = el

    element = property(_getElem, _setElem, "type of atom")

# End class AtomParSet


def _latgetter(par):

    def f(lat):
        return getattr(lat, par)

    return f

def _latsetter(par):

    def f(lat, value):
        setattr(lat, par, value)
        lat.setLatPar()
        return

    return f


class LatticeParSet(ParameterSet):
    """A wrapper for diffpy.Structure.Lattice.

    This class derives from diffpy.srfit.fitbase.parameterset.ParameterSet. See
    this class for base attributes.

    Attributes
    lattice     --  The diffpy.Structure.Lattice this is adapting
    name        --  Always "lattice"
    angunits    --  "deg", the units of angle

    Managed Parameters:
    a, b, c, alpha, beta, gamma --  The lattice parameters (ParameterAdapter).
    
    """

    def __init__(self, lattice):
        """Initialize

        lattice --  A diffpy.Structure.Lattice instance

        """
        ParameterSet.__init__(self, "lattice")
        self.angunits = "deg"
        self.lattice = lattice
        l = lattice
        self.addParameter(ParameterAdapter("a", l, _latgetter("a"),
            _latsetter("a")))
        self.addParameter(ParameterAdapter("b", l, _latgetter("b"),
            _latsetter("b")))
        self.addParameter(ParameterAdapter("c", l, _latgetter("c"),
            _latsetter("c")))
        self.addParameter(ParameterAdapter("alpha", l, _latgetter("alpha"),
            _latsetter("alpha")))
        self.addParameter(ParameterAdapter("beta", l, _latgetter("beta"),
            _latsetter("beta")))
        self.addParameter(ParameterAdapter("gamma", l, _latgetter("gamma"),
            _latsetter("gamma")))

        # Other setup
        self.__repr__ = l.__repr__
        return

# End class LatticeParSet

class StructureParSet(BaseStructure):
    """A wrapper for diffpy.Structure.Structure.

    This class derives from diffpy.srfit.fitbase.parameterset.ParameterSet. See
    this class for base attributes.

    Attributes:
    atoms   --  The list of AtomParSets, provided for convenience.
    stru    --  The diffpy.Structure.Structure this is adapting

    Managed ParameterSets:
    lattice     --  The managed LatticeParSet
    <el><idx>   --  A managed AtomParSets. <el> is the atomic element and <idx>
                    is the index of that element in the structure, starting
                    from zero. Thus, for nickel in P1 symmetry, the managed
                    AtomParSets will be named "Ni0", "Ni1", "Ni2" and "Ni3".
    
    """

    def __init__(self, stru, name):
        """Initialize

        stru    --  A diffpy.Structure.Structure instance

        """
        ParameterSet.__init__(self, name)
        self.stru = stru
        self.addParameterSet(LatticeParSet(stru.lattice))
        self.atoms = []

        cdict = {}
        for a in stru:
            el = a.element.title()
            # Try to sanitize the name.
            el = el.replace("+","p")
            el = el.replace("-","m")
            i = cdict.get(el, 0)
            aname = "%s%i"%(el,i)
            cdict[el] = i+1
            atom = AtomParSet(a, aname)
            self.addParameterSet(atom)
            self.atoms.append(atom)

        # other setup
        self.__repr__ = stru.__repr__
        return

    def getLattice(self):
        """Get the ParameterSet containing the lattice Parameters."""
        return self.lattice

    @classmethod
    def canAdapt(self, stru):
        """Return whether the structure can be adapted by this class."""
        from diffpy.Structure import Structure
        return isinstance(stru, Structure)

    def getScatterers(self):
        """Get a list of ParameterSets that represents the scatterers.

        The site positions must be accessible from the list entries via the
        names "x", "y", and "z". The ADPs must be accessible as well, but the
        name and nature of the ADPs (U-factors, B-factors, isotropic,
        anisotropic) depends on the adapted structure.

        """
        return self.atoms

    def getSpaceGroup(self):
        """Get the HM space group symbol for the structure."""
        return "P 1"

    def restrainBVS(self, prefactor = 1, scaled = False):
        """Restrain the bond-valence sum to zero.

        This adds a penalty to the cost function equal to
        prefactor * bvrmsdiff
        where bvrmsdiff is the rmsdifference between the calculated and
        expected bond valence sums for the structure. If scaled is true, this
        is also scaled by the current chi^2 value so the restraint is roughly
        equally weighted in the fit.

        prefactor   --  A multiplicative prefactor for the restraint 
                        (default 1).
        scaled  --  A flag indicating if the restraint is scaled (multiplied)
                    by the unrestrained point-average chi^2 (chi^2/numpoints)
                    (default False).

        Returns the BVSRestraint object for use with the 'unrestrain' method.

        """
        from .bvsrestraint import BVSRestraint

        res = BVSRestraint(self.stru)
        res.restrain(prefactor, scaled)
        self._restraints.add(res)
        # Our configuration changed. Notify observers.
        self._updateConfiguration()
        return res




# End class StructureParSet

__id__ = "$Id$"

