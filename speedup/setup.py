# from distutils.core import setup
# from distutils.extension import Extension
# from Cython.Distutils import build_ext
#
# ext_modules = [Extension("solve", ["solve.pyx", "QuadRootsRevG.cpp"], language='c++',)]
#
# setup(cmdclass = {'build_ext': build_ext}, ext_modules = ext_modules)
#
#

import numpy
from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration


config = Configuration('solve', '', '')
config.add_extension('solve',
                     language="c++",
                     sources=["solve.cpp", "QuadRootsRevG.cpp"],
                     extra_compile_args=["-std=c++11"],
                     extra_link_args=["-std=c++11"])
setup(**config.todict())
