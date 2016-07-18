#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
'''Sanity check for refcount'''
from __future__ import print_function

import mix
import sys

initial = sys.getrefcount(mix.Fiber)

def noop():
    pass

count = initial
fibers = []
for __ in range(10):
    fibers.append(mix.Fiber(noop))
    count += 1
    assert count == sys.getrefcount(mix.Fiber)

del fibers
assert initial == sys.getrefcount(mix.Fiber)
