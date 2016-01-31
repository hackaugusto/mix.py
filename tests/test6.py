#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
'''This test makes sure that we can deallocate a Fiber() without segfaulting'''
from __future__ import print_function

import mix

def noop():
    pass

f1 = mix.Fiber(noop)
del f1
