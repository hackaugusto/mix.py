# -*- coding: utf8 -*-
import mix


__all__ = (
    'switch_to',
)

def noop():
    raise RuntimeError('The main context was called')
    pass


main = mix.Fiber(noop)
current = main


def switch_to(fiber, *args, **kwargs):
    last = current
    current = fiber
    return mix.exchange(last, fiber, args, kwargs)
