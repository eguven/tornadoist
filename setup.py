import os
from setuptools import setup

setup(
    name = "tornadoist",
    version = "0.5.2",
    author = "Eren G\xc3\xbcven",
    author_email = "erenguven0@gmail.com",
    description = "mixins for tornado",
    license = "Apache License, Version 2",
    keywords = ["tornado", "celery"],
    url = "https://github.com/eguven/tornadoist.git",
    packages = ['tornadoist',],
    long_description = open("README.rst").read(),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
)
