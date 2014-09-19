# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 02:07:32 2014

@author: fanbin
"""

import numpy
import pandas

def talib_apply(panel, code, obj, functor):
    """
    """
    ret = functor( numpy.array(panel.ix[code,:,obj]))
    return pandas.DataFrame(ret, index=panel.index)