# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 16:01:52 2016

@author: amarty
"""

import json
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.pyplot as plt
from descartes import PolygonPatch

import dataloader
import geoconvert
from colorutils import cyclic_colors


def load_base_collection():
    with open(dataloader.get_path("secteurs-scolaires.geojson"), "r") as geofile:
        geojson_data = json.load(geofile)
    
    return geoconvert.FeatureCollection.from_mapping(geojson_data)


def extract_polys(fc):
    base_polys = []
    for feat in fc.features:
        base_polys.extend(list(feat.geometry.geoms))
    return base_polys


def plot_polys(fig, polys, color=None):
    if color is None:
        patches = [PolygonPatch(p) for p in polys]
    else:
        try:
            patches = [PolygonPatch(p, fc=c) for p, c in zip(polys, color)]
        except:
            patches = [PolygonPatch(p, fc=color) for p in polys]
    for patch in patches:
        fig.add_patch(patch)
    return fig


def plot_geom(fig, geom, color=None):
    if isinstance(geom, Polygon):
        if color is None:
            patch = PolygonPatch(geom)
        else:
            patch = PolygonPatch(geom, fc=color)
        fig.add_patch(patch)
        return fig
    elif isinstance(geom, MultiPolygon):
        return plot_polys(fig, geom.geoms, color)


def remove_geom_holes(geom):
    if isinstance(geom, Polygon):
        return Polygon(geom.exterior)
    elif isinstance(geom, MultiPolygon):
        return MultiPolygon([Polygon(p.exterior) for p in geom])


def simplify_geom(geom, eps=0.0005, remove_holes=True, simplify=True):
    simple = (geom.buffer(eps, resolution=2, cap_style=2)
                  .buffer(-eps, resolution=2, join_style=2))
    if remove_holes:
        simple = remove_geom_holes(simple)
    if simplify:
        simple = simple.simplify(eps)
    return simple

if __name__ == "__main__":
#    base_fc = load_base_collection()
#    sectors = pd.DataFrame([(feat.geometry, feat.properties["geometry_id"])
#                            for feat in base_fc.features],
#                           columns=["geom", "id"])
#    sectors["simple_geom"] = sectors["geom"].apply(simplify_geom)
    
    fig = plt.figure(figsize=(18, 16))
    ax = fig.gca()
    
    colors = cyclic_colors(len(sectors))
    for i in range(len(sectors)):
        plot_geom(ax, sectors["simple_geom"].iloc[i], colors[i])
    
    ax.axis("scaled")
    plt.show()