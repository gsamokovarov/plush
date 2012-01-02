#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup


def dependencies_from(filename):
    with open(join(abspath(dirname(__file__)), filename)) as file:
        return [line.strip() for line in file]

version = '0.1.0'

setup(
    name='plush_web',
    version=version,
    description='Micro framework inspirated by Sinatra, Express and Flask.',
    author='Genadi Samokovarov',
    author_email='gsamokovarov@gmail.com',
    packages = ['plush', 'plush.util', 'plush.util.compat'],
    url='https://github.com/gsamokovarov/plush',
    download_url='https://github.com/gsamokovarov/plush/tarball/%s' % version,
    license='http://www.apache.org/licenses/LICENSE-2.0',
    install_requires=dependencies_from('requirements.txt')
)
