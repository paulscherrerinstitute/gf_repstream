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
    namespace_packages=[],
    entry_points={},
    scripts=[],
    package_data = {'gf_repstream': ['static/repstream_config.json']},
    license="GNU GPLv3",
)
