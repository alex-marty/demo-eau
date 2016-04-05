# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 09:35:55 2016

@author: amarty
"""

from shapely.geometry import Polygon, MultiPolygon

from maputils import to_web_mercator


def geom_to_mercator(geom):
    if isinstance(geom, Polygon):
        return Polygon(
            map(to_web_mercator, geom.exterior.coords),
            [map(to_web_mercator, h.coords) for h in geom.interiors])
    elif isinstance(geom, MultiPolygon):
        return MultiPolygon([geom_to_mercator(p) for p in geom])
    else:
        raise ValueError("Unsupported geom type: {}".format(type(geom)))


class Patch(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_points(cls, points):
        return Patch(zip(*points))
        
    @classmethod
    def from_poly(cls, poly):
        """ WARNING: Drops the interiors """
        return cls(*poly.exterior.xy)
    
    def __repr__(self):
        return "Patch({})".format([list(self.x), list(self.y)])
    
    def to_list(self):
        return [list(self.x), list(self.y)]


class MultiPatch(object):
    def __init__(self, patches):
        self.patches = patches
    
    @classmethod
    def from_multipoly(cls, multipoly):
        """ WARNING: Drops polygons' interiors """
        return cls([Patch.from_poly(p) for p in multipoly])
    
    def __repr__(self):
        return "MultiPatch({})".format(list(self.patches))
    
    def to_list(self):
        return list(zip(*[p.to_list() for p in self.patches]))
    

def geom_to_list(geom):
    if isinstance(geom, Polygon):
        return Patch.from_poly(geom).to_list()
    elif isinstance(geom, MultiPolygon):
        return MultiPatch.from_multipoly(geom).to_list()
    else:
        raise ValueError("Unsupported geom type: {}".format(type(geom)))
    