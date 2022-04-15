#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

from fmexp.extensions import db
from fmexp.models import (
    User,
    DataPoint,
    DataPointDataType,
)


NUM_BINS = 50


def mouse_hist():
    data = []
    data2 = []

    for u in User.query_filtered(data_type=DataPointDataType.MOUSE.value):
        acs = u.get_mouse_action_chains()['action_chains']
        data.append(len(acs))
        for ac in acs:
            ac_len = len(ac)
            if ac_len > 20:
                data2.append(ac_len)

    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.hist(data, bins=NUM_BINS, linewidth=0.5, edgecolor="white")
    ax2.hist(data2, bins=NUM_BINS, linewidth=0.5, edgecolor="white")

    ax1.set_xlabel('AC length')
    ax1.set_ylabel('#')

    ax2.set_xlabel('Action length')
    ax2.set_ylabel('#')

    plt.show()
