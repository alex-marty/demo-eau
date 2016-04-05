# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 16:03:24 2016

@author: amarty
"""

import numpy as np
import pandas as pd
import shapely.geometry
from shapely.geometry import Polygon, MultiPolygon
import json

import dataloader
import maputils
from geoutils import geom_to_list


class Feature(object):
    type = "Feature"
    
    def __init__(self, geometry, properties):
        self.geometry = geometry
        self.properties = properties
    
    @classmethod
    def from_mapping(cls, mapping):
        if not set(mapping.keys()) == set(["type", "geometry", "properties"]):
            raise ValueError()
        if mapping["type"] != cls.type:
            raise ValueError()
        geometry = shapely.geometry.shape(mapping["geometry"])
        return cls(geometry, mapping["properties"])


class FeatureCollection(object):
    type = "FeatureCollection"
    
    def __init__(self, features):
        self.features = features
    
    @classmethod
    def from_mapping(cls, mapping):
        if not set(mapping.keys()) == set(["type", "features"]):
            raise ValueError()
        if mapping["type"] != cls.type:
            raise ValueError()
        features = [Feature.from_mapping(feat) for feat in mapping["features"]]
        return cls(features)


def geom_to_str(geom):
    return json.dumps(shapely.geometry.mapping(geom))
    


def extract_city_blocks(sectors_fc):
    blocks = pd.DataFrame(columns=["sector_id", "geo_shape", "centroid"])
    for sector in sectors_fc.features:
        sector_id = sector.properties["geometry_id"]
        geo_shapes = [json.dumps(shapely.geometry.mapping(geom))
                      for geom in sector.geometry.geoms]
        centroids = [json.dumps(shapely.geometry.mapping(geom.centroid))
                     for geom in sector.geometry.geoms]
        blocks = blocks.append(
                pd.DataFrame({"sector_id": [sector_id] * len(geo_shapes),
                              "geo_shape": geo_shapes,
                              "centroid": centroids}),
            ignore_index=True)
    blocks.sector_id = blocks.sector_id.astype(int)
    return blocks
            

def convert_sectors_to_blocks(data_file, output_file):
    with open(dataloader.get_path(data_file), "r") as geo_file:
        json_data = json.loads(geo_file.read())
    fc = FeatureCollection.from_mapping(json_data)
    blocks = extract_city_blocks(fc)
    blocks["id"] = blocks.index
    blocks.to_json(dataloader.get_path(output_file, verify_existing=False),
                   orient="records")


def convert_geo_to_patches(geo_df):
    patch_df = pd.DataFrame(columns=["sector_id", "patch_xs", "patch_ys"])
    for idx, sector in geo_df.iterrows():
        patches = geom_to_list(sector["geo_shape"])
        if isinstance(sector["geo_shape"], Polygon):
            sector_df = pd.DataFrame({
                "patch_xs": [patches[0]],
                "patch_ys": [patches[1]],
                "sector_id": sector["id"]})
        elif isinstance(sector["geo_shape"], MultiPolygon):
            sector_df = pd.DataFrame({
                "patch_xs": patches[0],
                "patch_ys": patches[1],
                "sector_id": np.repeat(sector["id"], len(patches[0]))})
        else:
            raise TypeError("Unsupported geo type: {}"
                            .format(type(sector["geo_shape"])))
        patch_df = patch_df.append(sector_df)
    patch_df["sector_id"] = patch_df["sector_id"].apply(int)
    patch_df.index = range(len(patch_df))
    return patch_df
