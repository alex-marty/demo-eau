# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 19:25:56 2016

@author: amarty
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import bokeh.palettes


def cyclic_colors(n, levels=20, color_map="Accent", format="rgb"):
    cmap = plt.get_cmap(color_map)
    colors = [cmap((i % levels) / float(levels - 1)) for i in range(n)]
    if format == "hex":
        return [matplotlib.colors.rgb2hex(col) for col in colors]
    else:
        return colors

def hex_colors(intensities, color_map="OrRd"):
    cmap = plt.get_cmap(color_map)
    return [matplotlib.colors.rgb2hex(cmap(z)) for z in intensities]

def scale_to_hex(scale, palette=bokeh.palettes.RdYlGn11):
    return palette[int(np.round(scale * (len(palette) - 1)))]

def scales_to_hex(scale_seq, palette=bokeh.palettes.RdYlGn11):
    return list(map(lambda s: scale_to_hex(s, palette), scale_seq))
