#!/usr/bin/env python

import io

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

import colorsys

from fmexp.extensions import db
from fmexp.models import (
    User,
    DataPoint,
    DataPointDataType,
)


def mouse_debug():

    u = User.query_filtered(data_type=DataPointDataType.MOUSE.value).first()

    mouse_features = u.get_mouse_features()
