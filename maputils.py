# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 17:45:04 2016

@author: amarty
"""

import numpy as np
from shapely.geometry import Polygon, MultiPolygon

from bokeh.models import WMTSTileSource


OSM_URL = 'http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png'
OSM_TILE_SOURCE = WMTSTileSource(url=OSM_URL, min_zoom=0, max_zoom=30)


def to_web_mercator(xLon, yLat=None):
    if yLat is None:
        yLat = xLon[1]
        xLon = xLon[0]
    # Check if coordinate out of range for Latitude/Longitude
    if (np.abs(xLon) > 180) and (np.abs(yLat) > 90):
        return
    semimajorAxis = 6378137.0  # WGS84 spheriod semimajor axis
    east = xLon * 0.017453292519943295
    north = yLat * 0.017453292519943295
    northing = 3189068.5 * np.log((1.0 + np.sin(north)) / (1.0 - np.sin(north)))
    easting = semimajorAxis * east
    return easting, northing


mercator_extent = dict(start=-20000000, end=20000000, bounds=None)

paris_extent_gps = dict(lat_range=(48.815, 48.90), lon_range=(2.255, 2.415))
paris_extent = {"sw_corner": to_web_mercator(paris_extent_gps["lon_range"][0],
                                             paris_extent_gps["lat_range"][0]),
                "ne_corner": to_web_mercator(paris_extent_gps["lon_range"][1],
                                             paris_extent_gps["lat_range"][1])}
paris_extent = {
    "x_range": (paris_extent["sw_corner"][0], paris_extent["ne_corner"][0]),
    "y_range": (paris_extent["sw_corner"][1], paris_extent["ne_corner"][1])}

def scale_seq(seq, scale):
    seq_mean = np.mean(seq)
    return [(x - seq_mean) * scale + seq_mean for x in seq]
            
def get_paris_extent(scale):               
    return {"x_range": scale_seq(paris_extent["x_range"], scale),
            "y_range": scale_seq(paris_extent["y_range"], scale)}