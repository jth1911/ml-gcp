from setuptools import find_packages
from setuptools import setup
import setuptools
import sys, os.path

from distutils.command.build import build as _build

setup(
    name='kfx',
    version='0.1',
    license='apache-2.0',
    packages=find_packages(),
    description = 'ML pipeline lib',
    include_package_data=True,
    install_requires=[
        'python-dotenv'
    ],
)