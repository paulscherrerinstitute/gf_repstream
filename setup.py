import re

from setuptools import find_packages, setup

with open("gf_repstream/__init__.py") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="gf_repstream",
    version=version,
    author="Leonardo Hax Damiani",
    author_email="leonardo.hax@psi.ch",
    description="Gigafrost stream repeater",
    packages=find_packages(),
    license="GNU GPLv3",
)