#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from __future__ import print_function

import mix

def noop():
    pass

main = mix.Fiber(noop)
fiber = mix.Fiber(noop)

mix.context_switch(main, fiber, 1)
