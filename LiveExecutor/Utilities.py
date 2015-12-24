# -*- coding: utf-8 -*-
u"""
Created on 2015-12-22

@author: cheng.li
"""


def sign(x):
    if x > 0.:
        return 1
    elif x < 0.:
        return -1
    else:
        return 0


def py_assert(condition, exception, msg):
    if not condition:
        raise exception(msg)
