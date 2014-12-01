
#!/usr/bin/env python

from setuptools import setup

setup(name='manipulators',
      version='0.1b',
      description='Tools to control electrophysiology manipulators',
      author='Joao Couto',
      author_email='jpcouto@gmail.com',
      url='https://github.com/jcouto/manipulators',
      packages=['manipulators'],
      entry_points={'console_scripts':
                    ['manipulators-control=manipulators.control:main'],
                },
      install_requires=[
          'pyserial',
          'argparse',
      ],
)
