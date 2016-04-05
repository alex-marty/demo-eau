# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 11:42:46 2016

@author: amarty
"""

from datetime import date

from bokeh.client import push_session
from bokeh.models import VBoxForm, HBox
from bokeh.io import curdoc
from bokeh.plotting import Figure, reset_output
from bokeh.models.widgets import DatePicker, Slider

reset_output()
session = push_session(curdoc())

slider = Slider(title="Hello", start=0, end=23, step=1, value=0)
picker = DatePicker(title="Test", min_date=date(2016, 1, 1),
                    max_date=date(2016, 1, 31), value=date(2016, 1, 1))

curdoc().add_root(VBoxForm(children=[picker]))
session.show()
