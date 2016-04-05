# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 18:01:07 2016

@author: amarty
"""

import os
import json
import socket
import numpy as np
import pandas as pd
import shapely.geometry


hostname_app_root_mapping = {
    "PC9074HFKY1": "W:\\workspace\\demo-eau",
    "hd-demo-w1": "/home/casd/demo-eau",
    "HP1040-1": "C:\\Users\\Utilisateur\\Dropbox\\Dev\\workspace\\demo-eau",
    "vps262755.ovh.net": "/home/alex/workspace/demo-eau"
}

APP_ROOT = hostname_app_root_mapping.get(socket.gethostname(),
                                         "W:\\workspace\\demo-eau")
DATA_DIR = os.path.join(APP_ROOT, "data")

data_info = {
        "geo_sectors": {
            "filename": "geo-sectors-simple-merc.json",
            "format": "json",
            "orient": "records"},
        "conso_sectors": {
            "filename": "conso-sectors-10m10d.json",
            "format": "json",
            "orient": "split"},
        "conso_sectors_perturbated": {
            "filename": "conso-sectors-p71-10m10d.json",
            "format": "json",
            "orient": "split"},
        "geo_sectors_patches": {
            "filename": "geo-sectors-simple-patches.json",
            "format": "json",
            "orient": "split"
        }
    }
    

def get_path(data_file, verify_existing=True):
    if verify_existing and data_file not in os.listdir(DATA_DIR):
        raise RuntimeError("Requested data file does not exist: {}"
                           .format(data_file))
    return os.path.join(DATA_DIR, data_file)


class DataLoader(object):
    def __init__(self, data_info):
        self.data_info = data_info
    
    def load(self, data_name):
        data_def = self.data_info[data_name]
        if data_def["format"] == "json":
            return self._load_json(data_def)
        else:
            raise ValueError("Unsupported file format: {}"
                             .format(data_def["format"]))
    
    def _load_json(self, data_def):
        return pd.read_json(get_path(data_def["filename"]),
                            orient=data_def["orient"])
    
    def save(self, data_name, df):
        data_def = self.data_info[data_name]
        if data_def["format"] == "json":
            return self._save_json(data_def, df)
        else:
            raise ValueError("Unsupported file format: {}"
                             .format(data_def["format"]))
    
    def _save_json(self, data_def, df):
        df.to_json(get_path(data_def["filename"], verify_existing=False),
                   orient=data_def["orient"])


dataloader = DataLoader(data_info)


def str_to_geo_shape(s):
    """ Converts a string representation of a geometric shape in GeoJSON format
    into a Shapely shape.
    """
    return shapely.geometry.shape(json.loads(s))
    

def load_city_blocks(data_file):
    """
    Reads a JSON input file and returns a data frame with the following
    columns:
    * id (int): city block's id
    * sector_id (int): id of the school sector the block belongs to
    * geo_shape (str, Polygon in GeoJSON format): Polygon shape of the block
    * centroid (str, Point in GeoJSON format): Point representing the centroid
        of the block
    """
    with open(get_path(data_file), "r") as geo_file:
        df = pd.DataFrame.from_dict(json.loads(geo_file.read()))
    df["geo_shape"] = df["geo_shape"].apply(str_to_geo_shape)
    df["centroid"] = df["centroid"].apply(str_to_geo_shape)
    return df


def load_city_blocks_patches(data_file):
    return pd.read_json(get_path(data_file), orient="records")


def load_geo_sectors():
    df = dataloader.load("geo_sectors")
    df["geo_shape"] = df["geo_shape"].apply(str_to_geo_shape)
    return df


# Hourly consumption in m^3/h
conso_type_paris_raw = pd.DataFrame([
        ("00:00:00", 21000),
        ("01:00:00", 17500),
        ("02:00:00", 14000),
        ("03:00:00", 12500),
        ("04:00:00", 11500),
        ("05:00:00", 12500),
        ("06:00:00", 15000),
        ("07:00:00", 34000),
        ("08:00:00", 47000),
        ("09:00:00", 44000),
        ("10:00:00", 40000),
        ("11:00:00", 38500),
        ("12:00:00", 36000),
        ("13:00:00", 35000),
        ("14:00:00", 36000),
        ("15:00:00", 32500),
        ("16:00:00", 32000),
        ("17:00:00", 31000),
        ("18:00:00", 34000),
        ("19:00:00", 36500),
        ("20:00:00", 34500),
        ("21:00:00", 32500),
        ("22:00:00", 27500),
        ("23:00:00", 26000)
    ], columns=["time", "conso"])

#conso_type_paris_raw.index = pd.DatetimeIndex(conso_type_paris_raw["time"])

conso_type_paris = conso_type_paris_raw["conso"]


def load_conso_data(data_file):
    """
    Reads a CSV input file and returns a data frame with the following columns:
    * date (datetime): datetime of the record
    * conso (float): water consumption in m^3/h
    * block_id (int): id of the block to which the record belongs
    """
    df = pd.DataFrame.from_csv(get_path(data_file))
    df["date"] = pd.to_datetime(df["date"])
    return df

def load_conso_sectors(data_file="conso_sectors_perturbed"):
    df = dataloader.load(data_file)
    df = df.set_index(["sector_id", "date"]).sort_index()
    return df
