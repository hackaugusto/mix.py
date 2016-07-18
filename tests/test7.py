#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from _abcoll import MutableMapping
import mix


class Ref(dict):
    def __init__(self):
        MutableMapping.update(self)

    def update(*args, **kwds):
        pass


def noop():
    pass


# this fails with 2.7.8
def instantiate():
    Ref()


main = mix.Fiber(noop)
fiber = mix.Fiber(instantiate)

mix.context_switch(main, fiber)
