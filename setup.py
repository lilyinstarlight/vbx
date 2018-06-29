#!/usr/bin/env python3
import os
import re

from setuptools import setup, find_packages


name = None
version = None


def find(haystack, *needles):
    regexes = [(index, re.compile("^{}\s*=\s*'([^']*)'$".format(needle))) for index, needle in enumerate(needles)]
    values = ['' for needle in needles]

    for line in haystack:
        if len(regexes) == 0:
            break

        for rindex, (vindex, regex) in enumerate(regexes):
            match = regex.match(line)
            if match:
                values[vindex] = match.groups()[0]
                del regexes[rindex]
                break

    return values


with open(os.path.join(os.path.dirname(__file__), 'vbx', '__init__.py'), 'r') as vbx:
    name, version = find(vbx, 'name', 'version')


setup(
    name=name,
    version=version,
    description='virtual branch exchange for interfacing with Twilio',
    license='MIT',
    url='https://github.com/fkmclane/vbx',
    author='Foster McLane',
    author_email='fkmclane@gmail.com',
    install_requires=['fooster-web', 'twilio', 'slixmpp', 'websockets'],
    packages=find_packages(),
    package_data={'': ['html/*.*', 'res/*.*']},
    entry_points = {'console_scripts': ['vbx = vbx.__main__:main']},
)
