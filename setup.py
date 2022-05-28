__version__ = '1.0'
from setuptools import setup, find_packages
from typing import List

# ---------- Setup  ------------------------------------------------------------------------------------------

import os

this_directory = os.path.abspath(os.path.dirname(__file__))
if os.path.exists(os.path.join(this_directory, 'README.md')):
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
        description = long_description.split('\n')[1]  # the first line is the description after the title
else:
    long_description = ''
    description = ''

if os.path.exists(os.path.join(this_directory, 'requirements.txt')):
    with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as fh:
        requirements: List[str] = [line.strip() for line in fh.read().split() if line and '#' not in line]
else:
    requirements = []

setup(
    name='gist-import',
    version=__version__,
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=requirements,
    url='https://github.com/matteoferla/gist-import',
    license='MIT',
    author='Matteo Ferla',
    author_email='matteo.ferla@gmail.com',
    classifiers=[  # https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',  #
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description=description,
    long_description=__doc__,
    long_description_content_type='text/markdown',
)
