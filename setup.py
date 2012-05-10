from setuptools import setup

setup(
    name='dargparse',
    version='0.1.0',
    author='ObjectLabs staff',
    author_email='staff@objectlabs.com',
    description='Declarative command-line argument parser for python',
    long_description="Declarative command-line argument parser for python",
    packages=['dargparse'],
    test_suite="dargparse.tests.test_suite",
    url='http://objectlabs.org',
    license='LICENSE.txt',
    install_requires=[
        'argparse==1.2.1'
    ]
)
