import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "tornadoist",
    version = "0.0.5",
    author = "Eren Güven",
    author_email = "josh.austin@gmail.com",
    description = ("mixins for tornado"),
    license = "Apache",
    keywords = "tornado",
    url = "https://github.com/eguven/tornadoist.git",
    packages=['tornadoist',],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache License",
    ],
)