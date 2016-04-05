# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 18:18:25 2016

@author: amarty
"""

from bokeh.models import Range1d
from bokeh.plotting import show, output_file, figure
from bokeh.models import WMTSTileSource
from bokeh.tile_providers import STAMEN_TONER

osm_url = 'http://a.tile.openstreetmap.org/{Z}/{X}/{Y}.png'
osm_tile_source = WMTSTileSource(url=osm_url, min_zoom=0, max_zoom=30)

mercator_extent = dict(start=-20000000, end=20000000, bounds=None)
x_range = Range1d(**mercator_extent)
y_range = Range1d(**mercator_extent)
map_plot = figure(tools='pan,wheel_zoom', x_range=x_range, y_range=y_range)
map_plot.add_tile(tile_source=osm_tile_source)

output_file("osm_minimal.html")
show(map_plot)
