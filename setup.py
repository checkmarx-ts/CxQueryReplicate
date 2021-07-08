from setuptools import setup

_version = '1.0.0'

install_requires = [
    'checkmarxpythonsdk'
]

tests_require = [
]

setup(
    name='cxqueryreplicate',
    version=_version,
    description='Checkmarx customized query replicator',
    url='https://github.com/checkmarx-ts/cxqueryreplicate',
    author='Checkmarx TS-APAC',
    author_email='TS-APAC-PS@checkmarx.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License v2.0',
        'Programming Language :: Python :: 3.7',
        'Topic :: CxSAST Administration :: Utilities',
    ],
    keywords='Checkmarx Query Replication',
    packages=['cxqueryreplicate'],
    python_requires='>=3.7',
    install_requires=install_requires,
    extras_require={
        'tests': install_requires + tests_require
    },
    package_data={'cxqueryreplicate': ['templates/*']},
    entry_points={
        'console_scripts':
        ['cxqueryreplicate=cxqueryreplicate.cxqueryreplicate:main']
    }
)
