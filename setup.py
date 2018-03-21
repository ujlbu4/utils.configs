#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

version = '0.0.6'

setup(
    name='configger',
    version=version,
    description="""pyhocon configs""",
    author='Ilya Shubkin',
    author_email='ilya.shubkin@gmail.com',
    url='https://github.com/ujlbu4/utils.configs',
    install_requires=[
        "pyhocon==0.3.38",
    ],
    license="MIT",
    zip_safe=False,
    packages=find_packages(exclude=["*tests*"]),

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    # include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: QA Developers',
        'Topic :: Software Development :: QA Testing Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
    ],
)
