#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from __future__ import print_function

import mix

def back():
    mix.context_switch(fiber, main)


def noop():
    pass

main = mix.Fiber(noop)
fiber = mix.Fiber(back)

mix.context_switch(main, fiber, [])
