from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.4'

install_requires = [
    'babel',
    'deskapi',
    'txlib-too',
]


setup(name='shuttle',
    version=version,
    description="A command-line interface for moving content between help desk and translation systems",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='',
    author='Nathan Yergler',
    author_email='nathan@eventbrite.com',
    url='http://github.com/eventbrite/localization_shuttle',
    license='Apache License v2',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['shuttle=shuttle.sync:main']
    },
)
