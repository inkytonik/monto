#!/usr/bin/env python3

from setuptools import setup

setup(name='Monto',
      version='0.1',
      description='A simple framework for building '
      + 'Disintegrated Development Environments',
      author='Tony Sloane',
      author_email='inkytonik@gmail.com',
      url='https://bitbucket.org/inkytonik/monto/',
      install_requires=['psutil', 'pyzmq'],
      scripts=['broker.py',
               'length.py',
               'monto.py',
               'print.py',
               'reflect.py',
               'reverse.py',
               'send.py',
               'wrap.py', ],
      py_modules=['montolib'])
