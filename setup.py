
#!/usr/bin/env python

from distutils.core import setup

setup(name='manipulators',
      version='0.1b',
      description='Tools to control electrophysiology manipulators',
      author='Joao Couto',
      author_email='jpcouto@gmail.com',
      url='https://github.com/jcouto/manipulators',
      packages=['manipulators'],
      install_requires=[
        'pyserial',
        ],
      )
