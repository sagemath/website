#!/usr/bin/env python

###########################################################################
# Copyright (c) 2010 Minh Van Nguyen <nguyenminh2@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# http://www.gnu.org/licenses/
###########################################################################

# README
#
# Updating the online list of Sage components. To use this script, run it thus:
#
# $ ./update_components.py

import copy
import os
from subprocess import PIPE, Popen
import sys

COMP_PAGE = os.path.abspath("../www/links-components.html")
STANDARD_DIR = os.path.abspath("../www/packages/standard")
COMP_LIST_START = "BEGIN COMPONENT LIST"
COMP_LIST_END = "END COMPONENT LIST"
# dictionaries of current packages
# Each package is described by the format
# spkg name without version number: (package name, URL, brief description)
SPKG = {
    "atlas": ("ATLAS", "http://math-atlas.sourceforge.net", "Automatically Tuned Linear Algebra Software"),
    "blas": ("BLAS", "http://www.netlib.org/blas/", "Basic Fortan 77 linear algebra routines"),
    "boehm_gc": ("boehm_gc", "http://www.hpl.hp.com/personal/Hans_Boehm/gc/", "The Boehm-Demers-Weiser conservative garbage collector"),
    "boost_cropped": ("Boost", "http://www.boost.org", "Free peer-reviewed portable C++ source libraries"),
    "cddlib": ("cddlib", "http://www.ifor.math.ethz.ch/~fukuda/cdd_home/", "Double description method of Motzkin et al."),
    "cephes": ("Cephes", "http://www.moshier.net", "Cephes mathematical library"),
    "cliquer": ("Cliquer", "http://users.tkk.fi/pat/cliquer.html", "Routines for clique searching"),
    "conway_polynomials": ("conway_polynomials", "http://www.math.rwth-aachen.de/~Frank.Luebeck/data/ConwayPol/index.html", "Frank L\\\"ubeck's tables of Conway polynomials over finite fields"),
    "cvxopt": ("CVXOPT", "http://abel.ee.ucla.edu/cvxopt/", "Convex optimization, linear programming, least squares, etc."),
    "cython": ("Cython", "http://www.cython.org", "C-Extensions for Python"),
    "docutils": ("Docutils", "http://docutils.sourceforge.net", "Open-source text processing system for processing plaintext documentation into useful formats, such as HTML or LaTeX"),
    "ecl": ("ECL", "http://ecls.sourceforge.net", "Embeddable Common-Lisp, an implementation of the Common Lisp language as defined by the ANSI X3J13 specification"),
    "eclib": ("eclib", "http://www.warwick.ac.uk/staff/J.E.Cremona/mwrank/index.html", "John Cremona's programs for enumerating and computing with elliptic curves defined over the rational numbers"),
    "ecm": ("GMP-ECM", "https://gforge.inria.fr/projects/ecm/", "Elliptic curve method for integer factorization"),
    "elliptic_curves": ("elliptic_curves", "http://www.warwick.ac.uk/~masgaj/ftp/data/", "Cremona's mini tables of elliptic curves"),
    "f2c": ("f2c", "http://www.netlib.org/f2c/", "Converts Fortran 77 to C code"),
    "fflas_ffpack": ("FFLAS-FFPACK", "http://linalg.org/projects/fflas-ffpack", "A LGPL-2.1+ source code library for dense linear algebra over word-size finite fields."),
    "flint": ("FLINT", "http://www.flintlib.org", "Fast Library for Number Theory"),
    "flintqs": ("flintqs", "http://www.friedspace.com/QS/", "William Hart's highly optimized multi-polynomial quadratic sieve for integer factorization"),
    "fortran": ("G95", "http://www.g95.org", "A stable, production Fortran 95 compiler available for multiple CPU architectures and operating systems"),
    "freetype": ("FreeType", "http://freetype.sourceforge.net/index2.html", "A free, high-quality, and portable font engine"),
    "gap": ("GAP", "http://www.gap-system.org", "Groups, Algorithms, Programming - a system for computational discrete algebra"),
    "gd": ("GD", "http://www.libgd.org", "Dynamic graphics generation tool"),
    "gdmodule": ("gdmodule", "http://newcenturycomputers.net/projects/gdmodule.html", "A Python interface to the GD library"),
    "genus2reduction": ("genus2reduction", "http://www.math.u-bordeaux.fr/~liu/G2R/", "Curve data computation"),
    "gf2x": ("GF2X", "http://gf2x.gforge.inria.fr/", "a C/C++ software package containing routines for fast arithmetic in GF(2)[x] (multiplication, squaring, GCD) and searching for irreducible/primitive trinomials."),
    "gfan": ("Gfan", "http://www.math.tu-berlin.de/~jensen/software/gfan/gfan.html", "Gr\\\"obner fans and tropical varieties"),
    "givaro": ("Givaro", "http://ljk.imag.fr/CASYS/LOGICIELS/givaro/", "C++ library for arithmetic and algebraic computations"),
    "glpk": ("GLPK", "http://www.gnu.org/software/glpk/glpk.html", "GNU Linear Programming Kit"),
    "gnutls": ("GnuTLS", "http://www.gnu.org/software/gnutls/", "The GNU Transport Layer Security Library"),
    "graphs": ("graphs", "http://good.math.iastate.edu/grout/graphs/", "A database of combinatorial graphs"),
    "gsl": ("GSL", "http://www.gnu.org/software/gsl/", "The GNU Scientific Library"),
    "iml": ("IML", "http://www.cs.uwaterloo.ca/~astorjoh/iml.html", "Integer Matrix Library"),
    "ipython": ("IPython", "http://ipython.scipy.org", "Interactive computing environment with an enhanced interactive Python shell"),
    "jinja": ("Jinja", "http://jinja.pocoo.org", "State of the art, general purpose template engine; slightly outdated version"),
    "jinja2": ("Jinja2", "http://jinja.pocoo.org", "State of the art, general purpose template engine; awesome version"),
    "lapack": ("LAPACK", "http://www.netlib.org/lapack/", "Linear Algebra PACKage written in Fortran"),
    "lcalc": ("lcalc", "http://pmmac03.math.uwaterloo.ca/~mrubinst/L_function_public/CODE/", "Michael Rubinstein's L-function calculator"),
    "libfplll": ("fplll", "http://perso.ens-lyon.fr/damien.stehle/index.html#software", "Euclidean lattice reduction"),
    "libgap": ("LibGAP", "https://bitbucket.org/vbraun/libgap", "LibGAP is essentially a fork of the upstream GAP kernel."),
    "libgcrypt": ("Libgcrypt", "http://directory.fsf.org/project/libgcrypt/", "General purpose cryptographic library based on the code from GnuPG"),
    "libgpg_error": ("Libgpg-error", "http://www.gnupg.org/related_software/libgpg-error/", "A small library that defines common error values for all GnuPG components"),
    "iconv": ("libiconv", "http://www.gnu.org/software/libiconv/", "A library to enable different languages with different characters to be handled properly"),
    "libpng": ("libpng", "http://www.libpng.org/pub/png/libpng.html", "Bitmap image support"),
    "linbox": ("LinBox", "http://www.linalg.org", "C++ template library for exact, high-performance linear algebra computation with dense, sparse, and structured matrices over the integers and over finite fields"),
    "libm4ri": ("M4RI", "http://m4ri.sagemath.org", "A library for fast arithmetic with dense matrices over GF(2)"),
    "libm4rie": ("M4RI(e)", "http://m4ri.sagemath.org", "A library for fast arithmetic with dense matrices over GF(2^e)"),
    "lrcalc": ("lrcalc", "http://math.rutgers.edu/~asbuch/lrcalc/", "Littlewood-Richardson Calculator "),
    "matplotlib": ("matplotlib", "http://matplotlib.sourceforge.net", "Python plotting library which produces publication quality figures in a variety of hardcopy formats and interactive environments across platforms"),
    "maxima": ("Maxima", "http://maxima.sourceforge.net", "System for manipulating symbolic and numerical expressions"),
    "mercurial": ("Mercurial", "http://mercurial.selenic.com", "Free, distributed source control management tool"),
    "moin": ("MoinMoin", "http://www.moinmo.in", "The MoinMoin wiki engine"),
    "mpc": ("GNU MPC", "http://www.multiprecision.org/", "Gnu Mpc is a C library for the arithmetic of complex numbers with arbitrarily high precision and correct rounding of the result."),
    "mpfi": ("MPFI", "http://perso.ens-lyon.fr/nathalie.revol/software.html", "Multiple precision interval arithmetic library based on MPFR"),
    "mpfr": ("MPFR", "http://www.mpfr.org", "C library for multiple-precision floating-point computations with correct rounding"),
    "mpir": ("MPIR", "http://www.mpir.org", "Multiple Precision Integers and Rationals"),
    "mpmath": ("mpmath", "http://mpmath.org/", "Pure Python library for multiprecision floating-point arithmetic"),
    "ncurses": ("ncurses", "http://invisible-island.net/ncurses", "a library of functions that manage an application's display on character-cell terminals (e.g., VT100)"),
    "networkx": ("NetworkX", "http://networkx.lanl.gov", "Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks"),
    "ntl": ("NTL", "http://www.shoup.net/ntl/", "A library for doing number theory"),
    "numpy": ("NumPy", "http://numpy.scipy.org", "Package for scientific computing with Python"),
    "opencdk": ("OpenCDK", "http://www.gnu.org/software/gnutls/", "Open Crypto Development Kit provides basic parts of the OpenPGP message format"),
    "palp": ("PALP", "http://hep.itp.tuwien.ac.at/~kreuzer/CY/CYpalp.html", "A package for analyzing lattice polytopes"),
    "pari": ("PARI/GP", "http://pari.math.u-bordeaux.fr", "computer algebra system for fast computations in number theory"),
    "patch": ("GNU patch", "http://savannah.gnu.org/projects/patch/", "Applies diffs and patches to files."),
    "pexpect": ("Pexpect", "http://www.noah.org/wiki/Pexpect", "Pure Python module that makes Python a better tool for controlling and automating other programs"),
    "pil": ("PIL", "http://www.pythonware.com/library/", "Python Imaging Library"),
    "polybori": ("PolyBoRi", "http://polybori.sourceforge.net", "Polynomials over Boolean Rings"),
    "polytopes_db": ("polytopes_db", "", "Reflexive Polytopes Databases that include lists of 2- and 3-dimensional reflexive polytopes"),
    "ppl": ("PPL", "http://bugseng.com/products/ppl/", "The Parma Polyhedra Library (PPL) provides numerical abstractions especially targeted at applications in the field of analysis and verification of complex systems."),
    "pycrypto": ("PyCrypto", "http://www.dlitz.net/software/pycrypto/", "The Python Cryptography Toolkit"),
    "pygments": ("Pygments", "http://pygments.org", "Generic syntax highlighter"),
    "pynac": ("Pynac", "http://pynac.org", "Symbolic computation with Python objects"),
    "python": ("Python", "http://www.python.org", "The Python programming language"),
    "python_gnutls": ("python-gnutls", "http://pypi.python.org/pypi/python-gnutls/", "Python wrapper for the GNUTLS library"),
    "r": ("R", "http://www.r-project.org", "A free software environment for statistical computing and graphics"),
    "rpy2": ("RPy2", "http://rpy.sourceforge.net/rpy2.html", "provides a low-level interface to R, a proposed high-level interface, including wrappers to graphical libraries, as well as R-like structures and functions."),
    "ratpoints": ("Ratpoints", "http://www.mathe2.uni-bayreuth.de/stoll/programs/", "Find rational points on hyperelliptic curves"),
    "readline": ("Readline", "http://tiswww.case.edu/php/chet/readline/rltop.html", "The GNU Readline library provides a set of functions for use by applications that allow users to edit command lines as they are typed in"),
    "rubiks": ("Rubik", "http://www.math.ucf.edu/~reid/Rubik/optimal_solver.html", "Optimal Rubik's cube solver"),
    "sagenb": ("SageNB", "http://nb.sagemath.org", "The Sage Notebook server"),
    "sagetex": ("SageTeX", "http://bitbucket.org/ddrake/sagetex", "The SageTeX package allows you to embed code, results of computations, and plots from the Sage mathematics software suite into LaTeX documents"),
    "scipy": ("SciPy", "http://www.scipy.org", "Scientific tools for Python"),
    "scipy_sandbox": ("scipy_sandbox", "", "This package builds some of the optional/experimental SciPy packages, currently including arpack and delaunay"),
    "scons": ("SCons", "http://www.scons.org", "An open source software construction tool"),
    "setuptools": ("setuptools", "http://pypi.python.org/pypi/setuptools/", "Download, build, install, upgrade, and uninstall Python packages -- easily!"),
    "singular-3-1": ("Singular", "http://www.singular.uni-kl.de", "Computer algebra system for polynomial computations, with special emphasis on commutative and non-commutative algebra, algebraic geometry, and singularity theory"),
    "sphinx": ("Sphinx", "http://sphinx.pocoo.org", "A tool that makes it easy to create intelligent and beautiful documentation"),
    "sqlalchemy": ("SQLAlchemy", "http://www.sqlalchemy.org", "Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL"),
    "sqlite": ("SQLite", "http://www.sqlite.org", "Software library that implements a self-contained, serverless, zero-configuration, transactional SQL database engine"),
    "symmetrica": ("Symmetrica", "http://www.algorithm.uni-bayreuth.de/en/research/SYMMETRICA/", " Collection of C routines for representation theory"),
    "sympow": ("SYMPOW", "", "Package to compute special values of symmetric power elliptic curve L-functions"),
    "sympy": ("SymPy", "http://code.google.com/p/sympy/", "Python library for symbolic mathematics"),
    "tachyon": ("Tachyon", "http://jedi.ks.uiuc.edu/~johns/raytracer/", "Parallel/multiprocessor ray tracing system"),
    "termcap": ("Termcap", "http://www.catb.org/~esr/terminfo/", "Simplifies the process of writing portable text mode applications"),
    "twisted": ("Twisted", "http://twistedmatrix.com/trac", "Event-driven networking engine written in Python"),
    "weave": ("weave", "http://www.scipy.org/Weave", "Tools for including C/C++ code within Python"),
    "zlib": ("zlib", "http://www.zlib.net", "Data compression library"),
    "zn_poly": ("zn_poly", "http://cims.nyu.edu/~harvey/code/zn_poly/", "C library for polynomial arithmetic in Z/nZ[x]"),
    "zodb3": ("ZODB", "http://www.zodb.org", "Native object database for Python"),
    "bzip2": ("bzip2", "http://www.bzip.org", "High-quality data compressor"),
    "gcc": ("gcc", "http://gcc.gnu.org/", "GCC, the GNU Compiler Collection"),
    "jmol": ("Jmol", "http://jmol.sourceforge.net", "Java viewer for chemical structures in 3D")
}
# these components are embedded into other packages
SPKG_EMBEDDED = {
    "jsmath": ("jsMath", "http://www.math.union.edu/~dpvc/jsMath/", "JavaScript implementation of LaTeX"),  # embedded in the moin spkg
    "mwrank": ("mwrank", "http://www.warwick.ac.uk/staff/J.E.Cremona/mwrank/", "Program for computing Mordell-Weil groups of elliptic curves over Q via 2-descent. Since November 2007 mwrank has formed part of the eclib package"),
    "rpy": ("RPy", "http://rpy.sourceforge.net", "Simple and efficient access to R from Python")  # embedded in the R spkg
}
# these packages should be excluded
SPKG_EXCLUDE = ["examples", "extcode", "sage", "sage_scripts", "sage_root"]

##############################
# helper functions
##############################


def current_spkgs(spkgdir, spkg_db, spkg_exclude):
    r"""
    Return a list of the current packages in the standard spkg repository.

    INPUT:

    - spkgdir -- the directory where the standard spkg's are located.

    - spkg_db -- the database of standard packages.

    - spkg_exclude -- the spkg's to ignore.

    OUTPUT:

    A list of the current standard packages. If the given repository contains
    an spkg not in the spkg database, we exit the script. In that case, you
    might want to add that missing spkg to the spkg database of this script.
    """
    # get list of current standard packages
    P = Popen("ls %s/*.spkg" % spkgdir, shell=True, stdout=PIPE)
    P = P.stdout.readlines()
    P = [os.path.basename(s.strip()) for s in P]
    # get rid of everything starting from the first dot "."
    P = [s[:s.find(".")] for s in P]
    # get rid of everything starting from the last dash "-"
    P = [s[:s.rfind("-")] for s in P]
    # determine those spkg's that are in the database of standard spkg's
    spkg = []
    for s in P:
        if s in spkg_db:
            spkg.append(s)
        elif s in spkg_exclude:
            continue
        else:
            print("Unknown package '%s'. Consider adding this spkg to the spkg database of this script. Then re-run the script. Exiting..." % s)
            sys.stdout.flush()
            sys.exit(1)
    return spkg


def replace_special(s):
    r"""
    Replace each special character from the spkg description with an
    equivalent that is suitable for display on web pages. The special
    characters we consider usually include escape sequences specific to LaTeX.

    INPUT:

    - s -- a string that describes an spkg.

    OUTPUT:

    A string the same as 's'. However, all special characters (LaTeX macros
    for special characters) are replaced with equivalent HTML codes.
    """
    replace_table = [
        ('\\"o', "&ouml;"),
        ('\\"u', "&uuml;")
    ]
    cleansed_str = copy.copy(s)
    for candidate, target in replace_table:
        cleansed_str = cleansed_str.replace(candidate, target)
    return cleansed_str


def update_page(f, spkg_current, spkg_db, spkg_embedded, sdelim, edelim):
    r"""
    Update the components page with the current list of standard spkg's.

    INPUT:

    - f -- the components page to update.

    - spkg_current -- the current list of standard packages.

    - spkg_db -- the database of standard packages.

    - spkg_embedded -- the list of packages that are embedded in other spkg's.

    - sdelim -- the delimiter signifying the start of the list of components.

    - edelim -- the delimiter signifying the end of the list of components.

    OUTPUT:

    Update the given components page with the current list of standard
    packages.
    """
    F = open(f, "r")
    # Exactly one of these three states must be true and the others false.
    # The state "start" denotes everything before the list of spkg's. The
    # state "middle" the list of spkg's. And the state "end" denotes
    # everything after the list of spkg's.
    start = True
    middle = False
    end = False
    page_start = ""
    page_middle = ""
    page_end = ""
    for line in F:
        line = line.strip()
        if sdelim in line:
            start = False
            middle = True
            end = False
        if edelim in line:
            start = False
            middle = False
            end = True
        if start:
            page_start = "".join([page_start, "\n", line])
        if middle:
            continue
        if end:
            page_end = "".join([page_end, "\n", line])
    F.close()
    page_start = "".join([page_start, "\n", "<!-- BEGIN COMPONENT LIST -->"])
    # get the package descriptions
    P = []
    for s in spkg_current:
        P.append(spkg_db[s])
    P += spkg_embedded.values()
    # sorting the list of packages, ignoring cases
    P = sorted(P, cmp=lambda x, y: cmp(x[0].lower(), y[0].lower()))
    page_middle = "".join([page_middle, "\n", "<ol>"])
    for s in P:
        # no URL provided for a component
        if s[1] == "":
            page_middle = "".join([
                page_middle,
                "\n",
                "<li>%s: %s</li>" % (s[0], replace_special(s[2]))])
        else:
            page_middle = "".join([
                page_middle,
                "\n",
                '<li><a target="_blank" href="%s">%s</a>: %s</li>' % (s[1], s[0], replace_special(s[2]))])
    page_middle = "".join([page_middle, "\n", "</ol>"])
    F = open(f, "w")
    F.write("".join([
        page_start.strip(),
        "\n",
        page_middle.strip(),
        "\n",
        page_end.strip()]))
    F.close()


def usage():
    """
    Print the usage information for this script.
    """
    print "".join(["Usage: ", sys.argv[0]])
    sys.stdout.flush()

##############################
# the script starts here
##############################

if __name__ == "__main__":
    # sanity checks
    if len(sys.argv) != 1:
        # this script currently doesn't accept any argument
        usage()
        sys.exit(1)
    if not os.path.isfile(COMP_PAGE):
        print("Invalid components page %s. Exiting..." % COMP_PAGE)
        sys.stdout.flush()
        sys.exit(1)
    if not os.path.isdir(STANDARD_DIR):
        print("Invalid standard spkg repository directory %s. Exiting..." % STANDARD_DIR)
        sys.stdout.flush()
        sys.exit(1)
    # now update the list of components
    update_page(
        COMP_PAGE,
        current_spkgs(STANDARD_DIR, SPKG, SPKG_EXCLUDE),
        SPKG,
        SPKG_EMBEDDED,
        COMP_LIST_START,
        COMP_LIST_END)
