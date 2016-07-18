#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
'''Checks that the fiber keeps a reference to the callback'''
from __future__ import print_function

import mix
import sys

initial = sys.getrefcount(mix.Fiber)

def noop():
    pass


class Callback(object):
    def __call__(self):
        mix.context_switch(first, main)

    def __del__(self):
        print('deleted')


current = sys.getrefcount(mix.Fiber)
assert current == initial

main = mix.Fiber(noop)
current +=1
assert sys.getrefcount(mix.Fiber) == current

first = mix.Fiber(Callback())
current +=1
assert current == sys.getrefcount(mix.Fiber)

# the fibers need to keep a reference to the callbacks and we need to run just
# fine
del Callback
assert current == sys.getrefcount(mix.Fiber)
mix.context_switch(main, first)

# there is a f1 reference in callback, keeping it alive, so the count doesnt
# decrease
del first
assert current == sys.getrefcount(mix.Fiber)

del main
assert current == sys.getrefcount(mix.Fiber)
