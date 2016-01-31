#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
'''Simplest test that switch back to the main thread and exit's cleanly'''
from __future__ import print_function

import mix

def first():
    print('first')
    mix.context_switch(f1, f2)

def second():
    print('second')

f1 = mix.Fiber(first)
f2 = mix.Fiber(second)

mix.context_switch(f2, f1)
