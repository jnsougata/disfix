import pathlib
from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='extslash',
    version='0.0.3',
    description='Integrates slash commands with discord.py 2.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='jnsougata',
    author=__author__,
    author_email='jnsougata@gmail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='discord.py, slash-commands, extslash-commands, python-discord-bot',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    install_requires=[],
    project_urls={
        'Bug Reports': 'https://github.com/jnsougata/ExtSlash/issues',
        'Source': 'https://github.com/jnsougata/ExtSlash',
    },
)
