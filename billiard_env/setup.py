import os

PACKAGE_NAME = 'billiard_env'


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration(PACKAGE_NAME, parent_package, top_path)
    config.add_subpackage('__check_build')
    config.add_subpackage('speedup')

    config.add_data_files('media/fonts')
    config.add_data_files('media/models')
    config.add_data_files('media/textures/')
    config.add_data_files('media/fonts/*')
    config.add_data_files('media/models/*')
    config.add_data_files('media/textures/*')

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
