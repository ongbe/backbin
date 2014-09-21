# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 02:07:32 2014

@author: fanbin
"""

import numpy
import pandas
import talib

    
def list_indicator_groups():
    """ list available indicator groups
        group: "Overlap", "Momentum","Volume","Volatility","Price",\
            "Cycle","Pattern"
    """
    return ["Overlap", "Momentum","Volume","Volatility","Price",\
    "Cycle","Pattern"]

def list_indicator(group=None):
    """ list all available indicators
    
    Parameters:
    -------
    group: string (optional)
        group of indicator; if none, function will list all indicators
    """
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
    """ list all available indicators
    
    Parameters:
    -------
    code: code of symbol (required)
        get help information of a symbol
    """
    if code is None:
        print "Usage: help_indicator(symbol), symbol is indicator name"
    else:
        if code.upper() not in talib.get_functions():
            print "ERROR: indicator "+code+" not in list"
            return
        else:
            func = talib.abstract.Function(code)
            print func
           
def get_indicator(data = None, indicator_name):
    """ Compute indicators
    
    Parameters:
    -------
    data: dataframe (optional)
        OHLCVA data
    
    indicator_name: string
        name of indicator, shold be get from list_indicators
    

    Return:
    -------
    if data is none, return the corresponding function object
    otherwise return computed dataframe containing indicators
    
    Notes:
    ------
    if data is None, return function object, so that you can apply 
    it and feed with parameters to gain more control; in the latter case, 
    indicator is applied with default parameters
    """
    if indicator_name.upper() not in talib.get_functions():
        print "ERROR: indicator "+indicator_name+" not in list"
        return
    else:
        if data is not None:
            data.columns = [s.lower() for s in data.columns]
            func = talib.abstract.Function(indicator_name)
            ret = func(data, price='open')
            data.columns = [s.title() for s in data.columns]
            return ret
        else:
            return talib.abstract.Function(indicator_name)
