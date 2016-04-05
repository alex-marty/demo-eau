# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 17:18:27 2016

@author: amarty
"""

import numpy as np
import pandas as pd

import dataloader


def add_slot(series, value, start=None, end=None):
    if start is None:
        start = series.index.min()
    if end is None:
        end = series.index.max()
    perturbation = pd.Series(np.repeat(0., len(series)), index=series.index)
    perturbation[start:end] = value
    return series + perturbation


def scale(series, value):
    m = series.mean()
    return (series - m) * value + m


def add_slot_and_scaling(series, slot_value, scale_value, start=None,
                         end=None):
    if start is None:
        start = series.index.min()
    if end is None:
        end = series.index.max()
    new_series = add_slot(series, slot_value, start, end)
    new_series[start:end] = scale(new_series[start:end], scale_value)
    return new_series
    

def add_saturation(series, value, start=None, end=None):
    if start is None:
        start = series.index.min()
    if end is None:
        end = series.index.max()
    new_series = series.copy(deep=True)
    new_series[start:end] = value
    return new_series
