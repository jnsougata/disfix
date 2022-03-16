import pathlib
from src.app_util import __version__, __author__
from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent.resolve()

with open('README.rst') as f:
    readme = f.read()

setup(
    name='app_util',
    version=__version__,
    description='Asynchronous Application Command wrapper for discord.py 2.0',
    long_description=readme,
    long_description_content_type="text/x-rst",
    project_urls={
        'Documentation': 'https://app-util.readthedocs.io/en/latest/',
        'Source': 'https://github.com/jnsougata/app_util'
    },
    author=__author__,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8.0',
    install_requires=[],
)
