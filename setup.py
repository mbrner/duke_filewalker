from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='duke_filewalker',
    version='0.0.1',

    description='Duke I\'m your Father!',
    long_description=long_description,

    url='https://github.com/mbrner/duke_filewalker',

    author='Mathis Boerner',
    author_email='mathis.boerner@tu-dortmund.de',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='unfolding',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
