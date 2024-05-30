"""A setuptools based setup module."""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(

    include_package_data=True,

    name='python-orai-backorai',  # Required

    version="0.2.0",  # Required

    description='',  # Optional

    url='https://github.alm.europe.cloudcenter.corp/sgt-orai/python-orai-backorai',  # Optional

    author='',  # Optional

    author_email='',  # Optional

    classifiers=[],

    keywords='',  # Optional

    # packages=find_packages(exclude=['data', 'tests']),  # Required
    packages=find_packages(),  # Required    

    python_requires='>=3.10',

    install_requires=[''],
)
