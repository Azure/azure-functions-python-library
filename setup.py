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
    packages=['azure.functions'],
    package_data={
        'azure.functions': ['py.typed']
    },
    install_requires=[
        'ujson~=4.0.1'
    ],
    extras_require={
        'dev': [
            'flake8~=3.7.9',
            'mypy',
            'pytest',
            'pytest-cov',
            'requests==2.*',
            'coverage'
        ]
    },
    include_package_data=True,
    test_suite='tests'
)
