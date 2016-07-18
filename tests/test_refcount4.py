#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
'''Checks that the fiber keeps a reference to the callback'''
from __future__ import print_function

import mix
import sys

def noop():
    pass


class Callback(object):
    def __call__(self):
        return_point = mix.context_switch(first, main)
        mix.context_switch(return_point, main)
        return main

    def __del__(self):
        print('deleted')


main = mix.Fiber(noop)
current +=1
assert sys.getrefcount(mix.Fiber) == current

first = mix.Fiber(Callback())
current +=1
assert current == sys.getrefcount(mix.Fiber)

second = mix.Fiber(noop)
current +=1
assert current == sys.getrefcount(mix.Fiber)

mix.context_switch(main, first)
mix.context_switch(main, first, second)

del first
assert current == sys.getrefcount(mix.Fiber)

mix.context_switch(main, second)

current -=1
assert current == sys.getrefcount(mix.Fiber)

del second
current -=1
assert current == sys.getrefcount(mix.Fiber)

del main
current -=1
assert current == sys.getrefcount(mix.Fiber)
