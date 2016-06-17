#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = '0.1'

import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-dataweb',
    version = VERSION,
    description='Linked Data support for Django environments. Focusses initially on linking django managed data to a reasoning environment with a SPARQL endpoint. This may just be metadata about native Django delivered endpoints.',
    packages=['dataweb'],
    include_package_data=True,
    author='Rob Atkinson',
    author_email='rob@metalinkage.com.au',
    license='BSD',
    long_description=read('README.md'),
    download_url='git://github.com/rob-metalinkage/django-dataweb.git',
    install_requires = ['django-skosxl>=0.1.0',
                        'django-rdf-io>=0.1.0',
                        'uriredirect'
                        ],
    dependency_links = [
        'git://github.com/rob-metalinkage/django-skosxl.git#egg=skosxl',
        'git://github.com/rob-metalinkage/django-rdf_io.git#egg=rdf_io',
        'git://github.com/rob-metalinkage/uriredirect.git#egg=uriredirect',
    ],
    zip_safe=False

)

