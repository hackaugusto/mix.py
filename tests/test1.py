#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
'''Tests a simple context switch that will end with a error of end-of-stack'''
from __future__ import print_function

import mix
import sys

def first():
    print('first')

def second():
    print('second')

f1 = mix.Fiber(first)
f2 = mix.Fiber(second)

mix.context_switch(f2, f1)
