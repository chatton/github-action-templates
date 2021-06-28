#!/usr/bin/env python3

from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="github-action-templates",
    version="0.0.4",
    description="Template GitHub Actions",
    author="Cian Hatton",
    author_email="cianhatton@gmail.com",
    url="https://github.com/chatton/GithubActionTemplates",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown'
)
