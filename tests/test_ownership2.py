#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from __future__ import print_function

import sys

import mix

def noop():
    pass


def test(*args, **kwargs):
    assert args[1] + 1 ==  sys.getrefcount(args[0])
    mix.context_switch(fiber, main, (args[1] + 1,))
    assert args[1] == sys.getrefcount(args[0]), 'the count should be one less, since we deleted the main ref'
    mix.context_switch(fiber, main)

main = mix.Fiber(noop)
fiber = mix.Fiber(test)

value = object()

args = [value, sys.getrefcount(value)]
assert 2 == args[1]
result, __ = mix.context_switch(main, fiber, value)

assert result[0] == sys.getrefcount(value[0])
args[0] = None
del args
mix.context_switch(main, fiber)

print('success')
