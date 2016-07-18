#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
'''Checks that the fiber keeps a reference to the callback'''
from __future__ import print_function

import mix
import sys


def noop():
    pass


def args(*args, **kwargs):              # value, args[0], frame
    v = args[0]                         # value, args[0], frame, v
    assert sys.getrefcount(v) == 5      # value, args[0], frame, v, getrefcount(object)
    mix.context_switch(fiber, main)     # value, args[0], frame, v, getrefcount(object)

    assert sys.getrefcount(v) == 4      # args[0], frame, v, getrefcount(object)
    mix.context_switch(fiber, main)     # args[0], frame, v, getrefcount(object)

    assert sys.getrefcount(v) == 3      # frame, v, getrefcount(object)
    mix.context_switch(fiber, main)     # frame, v, getrefcount(object)


main = mix.Fiber(noop)
fiber = mix.Fiber(args)

value = object()                        # value
assert sys.getrefcount(value) == 2      # value, getrefcount(object)
args = (value,)                         # value, args[0]
assert sys.getrefcount(value) == 3      # value, args[0], getrefcount(object)
mix.context_switch(main, fiber, args)   # value, args[0]

                                        # value, args[0], frame, v, getrefcount(object)
del value                               # args[0], frame, v, getrefcount(object)
mix.context_switch(main, fiber)         # args[0], frame, v, getrefcount(object)

                                        # args[0], frame, v, getrefcount(object)
del args                                # frame, v, getrefcount(object)
mix.context_switch(main, fiber)         # frame, v, getrefcount(object)
