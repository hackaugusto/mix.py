#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from __future__ import print_function

from collections import OrderedDict

import mix


def sorted_dict(kwds):
    result = OrderedDict()
    for key in sorted(kwds.keys()):
        result[key] = kwds[key]
    return result


def noop():
    pass


def args(*args, **kwargs):
    print(args, sorted_dict(kwargs))
    mix.context_switch(fiber, main)


main = mix.Fiber(noop)
fiber = mix.Fiber(args)

mix.context_switch(main, fiber, (1, 2), {'a': 1, 'b': 2})
