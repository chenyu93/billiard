import numpy


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('speedup', parent_package, top_path)
    config.add_extension('solve',
                         language="c++",
                         sources=["solve.cpp", "QuadRootsRevG.cpp"],
                         extra_compile_args=["-std=c++11"],
                         extra_link_args=["-std=c++11"])
    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
