import re

from setuptools import setup

with open("gf_repstream/__init__.py") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="gf_repstream",
    version=version,
    author="Leonardo Hax Damiani",
    author_email="leonardo.hax@psi.ch",
    description="Gigafrost stream repeater",
    packages=['gf_repstream'],
    license="GNU GPLv3",
)
