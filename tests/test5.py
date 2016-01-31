#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from __future__ import print_function

import mix

def first():
    print('first')
    mix.context_switch(f1, f2)
    print('second')
    mix.context_switch(f1, f2)
    print('third')
    mix.context_switch(f1, main)

def second():
    print('jump')
    mix.context_switch(f2, f1)
    print('jump')
    mix.context_switch(f2, f1)

def noop():
    pass

main = mix.Fiber(noop)
f1 = mix.Fiber(first)
f2 = mix.Fiber(second)

mix.context_switch(main, f1)
