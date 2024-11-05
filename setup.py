from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
sys.path.append("./pidog")
from version import __version__

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pidog',
    version=__version__,
    description='Picrawler gait Library for Raspberry Pi',
    long_description=long_description,
    url='https://github.com/sunfounder/pidog',
    author='SunFounder',
    author_email='service@sunfounder.com',
    license='GNU',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU License',
        'Programming Language :: Python :: 3',
    ],
    keywords='python raspberry pi GPIO sunfounder',
    packages=find_packages(exclude=['doc', 'tests*', 'examples']),
    install_requires=['robot_hat>=2.0.0', 'readchar', 'numpy'],
    entry_points={
        'console_scripts': [
            'pidog=pidog:__main__',
        ],
    },
)