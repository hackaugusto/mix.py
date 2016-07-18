#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
import __future__
import mix


class Ref(object):  # any primite trigger the error
    pass


def noop():
    pass


# this fails with 2.7.8
def exception():
    raise Exception()


main = mix.Fiber(noop)
fiber = mix.Fiber(exception)
mix.context_switch(main, fiber)
