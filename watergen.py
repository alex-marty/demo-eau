# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:39:26 2016

@author: amarty
"""

from datetime import datetime, date, time, timedelta
import numpy as np
import pandas as pd

import dataloader


class DailyConsoGenerator(object):
    sample_freq = {"low": pd.offsets.Hour(1),
                   "mid": pd.offsets.Minute(10),
                   "high": pd.offsets.Minute(1)}
    noise_scale = {"low": 1500, "mid": 750, "high": 100}
    
    def __init__(self, ref_data):
        if len(ref_data) != 24:
            raise ValueError("Reference data length should be 24, not {}"
                             .format(len(ref_data)))
        self.ref_data = ref_data
    
    def generate_day_base(self, day_date=datetime.now().date()):
        return pd.Series(self.ref_data.data,
                         index=pd.date_range(day_date, freq="H", periods=24))

    def _resample_date_range(self, date_range, freq):
        orig_freq_str = pd.infer_freq(date_range)
        orig_freq = pd.tseries.frequencies.to_offset(orig_freq_str)
        min_date = date_range[0]
        max_date = date_range[-1] + orig_freq
        return pd.date_range(min_date, max_date, freq=freq, closed="left")
    
    def _resample(self, series, freq, rescale=False):
        new_date_range = self._resample_date_range(series.index, freq)
        resampled = (pd.Series(series, index=new_date_range)
                       .interpolate(method="time"))
        if rescale:
            resampled /= float(len(resampled)) / len(series)
        return resampled      
    
    def generate_real(self, n_days, start_date=datetime.now().date(),
                      freq="mid"):
        return (self.generate_base(n_days, start_date, freq) +
                self.generate_noise(n_days, start_date, freq))
    
    def generate_noise(self, n_days, start_date=datetime.now().date(),
                       freq="mid"):
        start_date = pd.Timestamp(start_date)
        end_date = start_date + timedelta(days=n_days - 1, hours=23)
        date_range = pd.date_range(start_date, end_date,
                                   freq=self.sample_freq["low"])
        noise = np.random.normal(0, self.noise_scale["low"], len(date_range))
        noise_ts = pd.Series(noise, index=date_range)
        start_len = len(noise_ts)
        if freq in ["mid", "high"]:
            noise_ts = self._resample(noise_ts, self.sample_freq["mid"])
            noise_ts += np.random.normal(0, self.noise_scale["mid"],
                                         len(noise_ts))
        if freq == "high":
            noise_ts = self._resample(noise_ts, self.sample_freq["high"])
            noise_ts += np.random.normal(0, self.noise_scale["high"],
                                         len(noise_ts))
        return noise_ts * (float(start_len) / len(noise_ts))
    
    def generate_base(self, n_days, start_date=datetime.now().date(),
                      freq="mid"):
        series = self.generate_day_base(day_date=start_date)
        for i in range(1, n_days):
            d = start_date + timedelta(days=i)
            series = series.append(self.generate_day_base(day_date=d))
        resampled = self._resample(series, self.sample_freq[freq])
        return resampled * (float(len(series)) / len(resampled))
    
    def generate_multi(self, n_days, start_date=datetime.now().date(),
                       freq="mid"):
        base = self.generate_base(n_days, start_date, freq)
        noise = self.generate_noise(n_days, start_date, freq)
        real = base + noise
        return pd.DataFrame({"real": real, "trend": base, "noise": noise})


def generate_conso_data(n_days):
    conso_data = pd.DataFrame(columns=["block_id", "date", "conso"])
    gen = DailyConsoGenerator(dataloader.conso_type_paris)
    city_blocks = dataloader.load_city_blocks("city-blocks-poly.json")
    for block_id in city_blocks["id"]:
        series = gen.generate_multi(n_days)
        conso_data = conso_data.append(pd.DataFrame({
            "block_id": np.repeat(block_id, len(series)),
            "date": series.index,
            "conso": series.data}))
    return conso_data


def generate_sectors_conso_data(n_days, start_date=date(2016, 3, 1),
                                freq="mid"):
    """ TODO: Vary conso scaling for different sectors """
    conso_data = pd.DataFrame(columns=["date", "sector_id", "real", "trend", 
                                       "noise"])
    gen = DailyConsoGenerator(dataloader.conso_type_paris)
    geo_sectors = dataloader.load_geo_sectors()
    scale = 1.0 / len(geo_sectors)
    for sector_id in geo_sectors["id"]:
        sector_data = gen.generate_multi(n_days, start_date) * scale
        conso_data = conso_data.append(pd.DataFrame({
                "date": sector_data.index,
                "sector_id": np.repeat(sector_id, len(sector_data)),
                "real": sector_data["real"],
                "trend": sector_data["trend"],
                "noise": sector_data["noise"],}),
            ignore_index=True)
    return conso_data

#if __name__ == "__main__":
#    d = generate_conso_data(2)