#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from __future__ import print_function

import mix


def noop():
    pass


def args(*args, **kwargs):
    print(args, kwargs)
    mix.context_switch(fiber, main)


main = mix.Fiber(noop)
fiber = mix.Fiber(args)

mix.context_switch(main, fiber, (), {'a': 1})
