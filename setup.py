# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys

from setuptools import find_packages, setup
from azure.functions import __version__

EXTRA_REQUIRES = {
    'dev': [
        'flake8-logging-format',
        'mypy',
        'pytest',
        'pytest-cov',
        'requests==2.*',
        'coverage',
        'azure-functions-durable'
    ]
}

if sys.version_info[:2] <= (3, 11):
    EXTRA_REQUIRES.get('dev').append(
        "flake8~=4.0.1"
    )
else:
    EXTRA_REQUIRES.get('dev').append(
        "flake8~=7.1.1"
    )

with open("README.md") as readme:
    long_description = readme.read()

setup(
    name='azure-functions',
    version=__version__,
    description='Azure Functions for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Environment :: Web Environment',
        'Development Status :: 5 - Production/Stable',
    ],
    license='MIT',
    packages=find_packages(exclude=[
        'azure', 'tests'
    ]),
    package_data={
        'azure.functions': ['py.typed']
    },
    extras_require=EXTRA_REQUIRES,
    include_package_data=True,
    test_suite='tests'
)
