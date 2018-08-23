from setuptools import setup


setup(
    name='azure-functions',
    version='1.0.0a4',
    description='Azure Functions for Python',
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
        'Development Status :: 3 - Alpha',
    ],
    license='MIT',
    packages=['azure.functions'],
    extras_require={
        'dev': [
            'flake8~=3.5.0',
            'mypy',
            'pytest',
            'requests==2.*',
        ]
    },
    include_package_data=True,
    test_suite='tests'
)
