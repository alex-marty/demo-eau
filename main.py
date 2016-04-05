# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 17:11:16 2016

@author: amarty
"""

print("Loading modules")
import sys
import os
from datetime import datetime
import numpy as np
import pandas as pd

from bokeh.client import push_session
from bokeh.models import (HBox, VBoxForm, VBox, ColumnDataSource,
                          DatetimeTickFormatter, CheckboxButtonGroup,
                          WMTSTileSource)
from bokeh.plotting import show, output_server, output_file, reset_output, Figure
from bokeh.io import curdoc
from bokeh.models.widgets import (Slider, TextInput, Button, Select, Panel,
                                  Tabs)
#from bokeh import palettes

sys.path.append(os.path.dirname(__file__))

from dataloader import load_geo_sectors, load_conso_sectors, dataloader
from maputils import get_paris_extent, OSM_URL
from colorutils import scales_to_hex

OSM_TILE_SOURCE = WMTSTileSource(url=OSM_URL, min_zoom=0, max_zoom=30)
PUBLISH_MODE = "app"

if PUBLISH_MODE == "session":
    reset_output()
    session = push_session(curdoc())

# Load data
print("Loading data")
geo_sectors = dataloader.load("geo_sectors_patches")
sector_ids = sorted(geo_sectors["sector_id"].unique())
n_sectors = len(sector_ids) # Sectors are 1-numbered and there are holes
n_patches = len(geo_sectors)

conso_sectors = load_conso_sectors("conso_sectors")
conso_sectors_pert = load_conso_sectors("conso_sectors_perturbated")
dates = conso_sectors.index.get_level_values("date")
conso_bounds = (conso_sectors_pert["real"].min(), conso_sectors_pert["real"].max())

geo_source = ColumnDataSource(data=dict(xs=[], ys=[], colors=[]))
conso_source = ColumnDataSource(data=dict(date=[], conso=[], diff=[]))
datetime_source = ColumnDataSource(data=dict(date=[], conso=[]))


# Inputs
print("Building page")
button = Button(label="Close")
sector_select = Select(title="Secteur", value="1",
                       options=list(map(str, range(1, n_sectors))))
date_slider = Slider(title="Date",
                     start=dates.min().day,
                     end=dates.max().day,
                     step=1,
                     value=dates.min().day)
time_slider = Slider(title="Heure", start=0, end=23, step=1, value=0)
type_button = CheckboxButtonGroup(labels=["Secteur", "Signal"], active=[0])


# Plots
class MapPlot(object):
    def __init__(self):
        self.map_plot = Figure(
            tools="pan,wheel_zoom,tap", toolbar_location="right",
            logo=None, min_border=0, min_border_left=0,
            **get_paris_extent(0.6), # x_range & y_range
            plot_width=1100, plot_height=650)
        self.map_plot.add_tile(tile_source=OSM_TILE_SOURCE)
        self.map_plot_renderer = self.map_plot.patches(
            source=geo_source,
            xs="xs",
            ys="ys",
            line_width=2,
            line_color=None,
            selection_line_color="firebrick",
            nonselection_line_color=None,
            fill_color="colors",
            selection_fill_color="colors",
            nonselection_fill_color="colors",
            alpha=0.85,
            selection_alpha=0.9,
            nonselection_alpha=0.85)
        self.map_plot.axis.visible = None
        self.map_plot_ds = self.map_plot_renderer.data_source
    
    def get_plot(self):
        return self.map_plot
    
    def get_data_source(self):
        return self.map_plot_ds


class ColorBar(object):
    def __init__(self):
        self.map_colorbar = Figure(tools="", toolbar_location=None,
                              min_border=0, min_border_right=0,
                              plot_width=80, plot_height=650,
                              x_range=(0., 1.), y_range=conso_bounds)
        self.map_colorbar.xaxis.visible = None
        self.map_colorbar.grid.grid_line_color = None
        colorbar_ys = np.linspace(conso_bounds[0], conso_bounds[1], 12)
        colorbar_colors = scales_to_hex(np.linspace(0., 1., 11))
        self.map_colorbar.quad(bottom=colorbar_ys[:-1], top=colorbar_ys[1:],
                          left=0., right=1.,
                          fill_color=colorbar_colors, line_color=None,
                          alpha=0.9)
    
    def get_plot(self):
        return self.map_colorbar


class ConsoPlot(object):
    def __init__(self):
        self.conso_plot = Figure(
            title="Consommation", toolbar_location="right",
            tools="pan,box_zoom,wheel_zoom,reset", 
            logo=None, min_border=0,
            plot_width=1200, plot_height=250,
            x_axis_type="datetime",
            x_range=(dates.min(), dates.max()),
            y_range=(0., conso_bounds[1]))
        self.sector_renderer = self.conso_plot.line(
            source=conso_source, x="date", y="conso",
            color="navy", alpha=0.7, line_width=1.5)
        self.signal_renderer = self.conso_plot.line(
            source=conso_source, x="date", y="diff",
            color="green", alpha=0.7, line_width=2)
        self.conso_plot.line(source=datetime_source, x="date", y="conso",
                             color="firebrick", line_width=2)
        self.conso_plot.xaxis[0].formatter = DatetimeTickFormatter(
            formats=dict(
                hours=["%d/%m"],
                days=["%d/%m"],
                months=["%d/%m"],
                years=["%d/%m"],
            )
        )
        self.conso_plot.xaxis.axis_label = "Date"
#        self.conso_plot.yaxis.axis_label = "m^3/h"
    
    def get_plot(self):
        return self.conso_plot
        
    def update_title(self, title):
        self.conso_plot.title = title
    
    def set_active(self, active):
        if 0 in active and self.sector_renderer not in self.conso_plot.renderers:
            self.conso_plot.renderers.append(self.sector_renderer)
        elif not 0 in active and self.sector_renderer in self.conso_plot.renderers:
            self.conso_plot.renderers.remove(self.sector_renderer)
        if 1 in active and self.signal_renderer not in self.conso_plot.renderers:
            self.conso_plot.renderers.append(self.signal_renderer)
        elif not 1 in active and self.signal_renderer in self.conso_plot.renderers:
            self.conso_plot.renderers.remove(self.signal_renderer)


map_plot = MapPlot()
map_colorbar = ColorBar()
conso_plot = ConsoPlot()

# Input behaviors
def get_patch_colors(sector_hour_conso):
    # Sectors are 1-numbered
    sector_z = sector_hour_conso.map(
        lambda x: (x - conso_bounds[0]) / (conso_bounds[1] - conso_bounds[0]))
    sector_z.index = sector_z.index.droplevel("date")
    patch_z = geo_sectors["sector_id"].map(lambda s_id: sector_z[s_id])
    return scales_to_hex(patch_z)
    
def update_sources(sector_id, conso_date, mode):
    sector_conso = conso_sectors.loc[sector_id, "real"]
    signal =  pd.rolling_mean(conso_sectors_pert.loc[sector_id, "real"] -
                              conso_sectors_pert.loc[sector_id, "trend"],
                              window=8) * 3
    conso_source.data = {
        "date": sector_conso.index,
        "conso": sector_conso,
        "diff": signal
    }
    conso_date = conso_date.replace(minute=0, second=0, microsecond=0)
    if 1 in mode:
        hour_conso = conso_sectors_pert.loc[(slice(None), conso_date), "real"]
    else:
        hour_conso = conso_sectors.loc[(slice(None), conso_date), "real"]
    colors = get_patch_colors(hour_conso)
    geo_source.data = {
        "xs": geo_sectors["patch_xs"],
        "ys": geo_sectors["patch_ys"],
        "colors": colors
    }
    datetime_source.data = {
        "date": [conso_date, conso_date],
        "conso": (0., conso_bounds[1])
    }
    title = "Consommation {}, {}".format(sector_id, conso_date)
    print(title)
    conso_plot.update_title(title)
    conso_plot.set_active(mode)

def update(attrname, old, new):
    print("update {} {} {}".format(attrname, old, new))
    sector_id = int(sector_select.value)
    conso_date = datetime(2016, 3, int(date_slider.value),
                          int(time_slider.value))
    update_sources(sector_id, conso_date, type_button.active)
sector_select.on_change("value", update)
date_slider.on_change("value", update)
time_slider.on_change("value", update)
type_button.on_change("active", update)

def on_selection_change(attr, old, new):
    print("on_selection_change")
    indices = new["1d"]["indices"]
    if indices:
        sector_id = geo_sectors.loc[indices[0]]["sector_id"]
        sector_select.value = str(sector_id) # Calls update in chain
        #update_sources(sector_id=sector_id)
map_plot.get_data_source().on_change("selected", on_selection_change)

def close_session():
    session.close()
button.on_click(close_session)


# Page build
inputs = VBoxForm(children=[sector_select, date_slider, time_slider,
                            type_button])
map_box = HBox(children=[map_colorbar.get_plot(), map_plot.get_plot()])
plots = VBox(children=[map_box, conso_plot.get_plot()])
root_element = HBox(children=[inputs, plots])

update(None, None, None) # Init data


# Session
print("Starting server")
curdoc().add_root(root_element)
if PUBLISH_MODE == "session":
    session.show()
    session.loop_until_closed()
print("Script ended")
