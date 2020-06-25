from setuptools import setup
from azure.functions import __version__


setup(
    name='azure-functions',
    version=__version__,
    description='Azure Functions for Python',
    long_description='Python support for Azure Functions is based on '
                     'Python3.[6|7|8], serverless hosting on Linux and the '
                     'Functions 2.0 and 3.0 runtime. This module provides the '
                     'rich binding definitions for Azure Functions for Python '
                     'apps.',
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
