import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "salest",
    version = "0.0.1",
    package_data = {
                    '': ['templates/*.html', 'templates/*/*.html']},
    author = "Alexandr Sorokin",
    author_email = "bsorokind@gmail.com",
    description = ("eCommerce framework for django."),
    license = "BSD",
    keywords = "example documentation tutorial",
    url = "http://salestproject.com",
    packages=find_packages(),
    long_description='README',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)