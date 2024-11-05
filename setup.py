from setuptools import setup, find_packages
import sys
import os

# Add the pidog directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "pidog"))
from version import __version__

setup(
    name='pidog',
    version=__version__,
    description='Picrawler gait Library for Raspberry Pi',
    author='nuvocode',
    author_email='nuvocode7@gmail.com', 
    url='https://github.com/nuvocode/pidog',
    packages=find_packages(),
    install_requires=[
        'robot_hat>=2.0.0',
        'readchar',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            'pidog=pidog:__main__'
        ]
    }
)