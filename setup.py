#!/usr/bin/env python3
from setuptools import setup, find_packages

from vbx import name, version

setup(
    name=name,
    version=version,
    description='virtual branch exchange for interfacing with Twilio',
    license='MIT',
    url='https://github.com/fkmclane/vbx',
    author='Foster McLane',
    author_email='fkmclane@gmail.com',
    install_requires=['twilio=6.0.0rc12', 'slixmpp'],
    packages=find_packages(),
    package_data={'': ['res/*.*']},
    entry_points = {'console_scripts': ['vbx = vbx.main']},
)
