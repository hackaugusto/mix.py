#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from __future__ import print_function

import sys

import mix

def noop():
    pass


def test(*args, **kwargs):
    assert 3 == sys.getrefcount(args[0]), 'the fiber must increment the refcount'
    mix.context_switch(fiber, main)

main = mix.Fiber(noop)
fiber = mix.Fiber(test)

value = (object(), )
assert 2 == sys.getrefcount(value[0])
mix.context_switch(main, fiber, value)
assert 3 == sys.getrefcount(value[0]), 'returning from the context _needs_ to leave the refcount'
print('success')
