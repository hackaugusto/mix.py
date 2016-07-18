#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
import sys

from setuptools import setup, find_packages, Extension

INCLUDE_DIRS = ['/usr/include']
LIBRARIES_DIRS = ['/usr/lib']

if sys.version_info > (3,):
    LIBRARIES = ['boost_python3', 'boost_context']
else:
    LIBRARIES = ['boost_python', 'boost_context']

COMPILE_ARGS = [
    '-g3',
    '-ggdb',
    '-Wall',
    '-Wextra',
    '-Werror',
    '-Wno-long-long',
    '-Wno-variadic-macros',
    '-fexceptions',
    '-DNDEBUG',
    '-std=c++14',
    '-O0',
    '-pipe',
    '-fstack-protector-strong',
    '--param=ssp-buffer-size=4',
]
LINKS_FLAGS = [
    '-Wl,-O1,--sort-common,--as-needed,-z,relro,--export-dynamic',
]

mix_extension = Extension(
    name='fiber',
    sources=['mix/fiber.cpp'],
    language='c++',
    include_dirs=INCLUDE_DIRS,
    library_dirs=LIBRARIES_DIRS,
    libraries=LIBRARIES,
    extra_compile_args=COMPILE_ARGS,
    extra_link_args=LINKS_FLAGS,
)


if __name__ == '__main__':
    setup(
        name='mix.py',
        version='0.0.1',
        packages=find_packages(),
        ext_modules=[mix_extension],
    )
