# -*- coding: utf-8 -*-

import io
import re

from setuptools import find_packages, setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("renoir_haml/__version__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

with io.open("requirements.txt", "rt", encoding="utf8") as f:
    requirements = f.readlines()


setup(
    name="Renoir-HAML",
    version=version,
    url="https://github.com/gi0baro/renoir-haml",
    project_urls={
        "Code": "https://github.com/gi0baro/renoir-haml",
        "Issue tracker": "https://github.com/gi0baro/renoir-haml/issues",
    },
    license="BSD-3-Clause",
    author="Giovanni Barillari",
    author_email="gi0baro@d4net.org",
    description="HAML syntax for Renoir templates",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    python_requires=">=3.6",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML"
    ]
)
