"""Setup module for Robot Framework Requests Logger Library package."""

# To use a consistent encoding
from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='robotframework-requestslogger',
    version='1.0.1',
    description='Robot Framework Requests Logging Library',
    long_description=long_description,
    url='https://github.com/peterservice-rnd/robotframework-requestslogger',
    author='JSC PETER-SERVICE',
    author_email='mf_aist_all@billing.ru',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Robot Framework :: Library',
    ],
    keywords='testing testautomation robotframework logging autotest requests http',
    package_dir={'': 'src'},
    py_modules=['RequestsLogger'],
    install_requires=[
        "robotframework",
        "six"
    ],
    extras_require={
        ':python_version<"3.2"': [
            'functools32>=3.2.3-2'
        ],
    }
)
