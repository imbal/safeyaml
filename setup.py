from setuptools import find_packages
from setuptools import setup

setup(
    name='safeyaml',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'PyYAML',
    ],
    entry_points={
        'console_scripts': {
            'safeyaml=safeyaml.cli:main',
        },
    },
)
