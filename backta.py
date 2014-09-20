# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 02:07:32 2014

@author: fanbin
"""

import numpy
import pandas
import talib

    
def list_indicator_groups():
    return ["Overlap", "Momentum","Volume","Volatility","Price","Cycle","Pattern"]

def list_indicator(group=None):
    if group is None:
        return talib.get_functions()
    else:
        if group in ["Overlap", "overlap", "over"]:
            return talib.get_function_groups()["Overlap Studies"]
        elif group is ["Momentum", "momentum", "momen", "mom"]:
            return talib.get_function_groups()["Momentum Indicators"]
        elif group is ["Volume", "volume", "volu", "vol"]:
            return talib.get_function_groups()["Volume Indicators"]
        elif group is ["Volatility", "volatility", "vola"]:
            return talib.get_function_groups()["Volatility Indicators"]
        elif group is ["Price", "price", "pri"]:
            return talib.get_function_groups()["Price Transform"]            
        elif group is ["Cycle", "cycle", "cyc"]:
            return talib.get_function_groups()["Cycle Indicators"]
        elif group is ["Pattern", "pattern", "patt", "pat"]:
            return talib.get_function_groups()["Pattern Recognition"]
        else:
            print "ERROR: no matching group "+group+", must be in: "
            print list_indicator_groups()
            print "Or enter no group to get full list of indicators:"
            print "  list_indicator()"
            return  

def help_indicator(code):
    if code is None:
        print "Usage: help_indicator(symbol), symbol is indicator name"
    else:
        if code.upper() not in talib.get_functions():
            print "ERROR: indicator "+code+" not in list"
            return
        else:
            func = talib.abstract.Function(code)
            print func
           
def get_indicator(panel, code, obj, functor):
    """
    """
    ret = functor( numpy.array(panel.ix[code,:,obj]))
    return pandas.DataFrame(ret, index=panel.index)