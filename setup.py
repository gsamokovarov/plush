#!/usr/bin/env python

from setuptools import setup


def dependencies_from(filename):
    with open(filename) as file:
        return [line.strip() for line in file]

setup(
    name='plush_web',
    version='0.1.0',
    description='Micro framework inspirated by Sinatra, Express and Flask.',
    author='Genadi Samokovarov',
    author_email='gsamokovarov@gmail.com',
    packages = ['plush', 'plush.util', 'plush.util.compat'],
    url='https://github.com/gsamokovarov/plush',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    install_requires=dependencies_from('requirements.txt')
)
