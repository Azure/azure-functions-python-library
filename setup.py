# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from setuptools import setup
from azure.functions import __version__

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
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Environment :: Web Environment',
        'Development Status :: 5 - Production/Stable',
    ],
    license='MIT',
    packages=['azure.functions'],
    package_data={
        'azure.functions': ['py.typed']
    },
    extras_require={
        'dev': [
            'flake8~=3.7.9',
            'mypy',
            'pytest',
            'requests==2.*',
            'coverage'
        ]
    },
    include_package_data=True,
    test_suite='tests'
)
