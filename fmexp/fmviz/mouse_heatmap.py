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



def user_mouse_heatmap(user, show=True):
    if show:
        fig, ax = plt.subplots()

    else:
        fig = Figure()
        ax = fig.subplots()

    # mouse_features = user.get_mouse_features()
    mouse_action_chains = user.get_mouse_action_chains()

    all_dps = []
    colors = []

    len_acs = len(mouse_action_chains['action_chains'])
    for i, ac in enumerate(mouse_action_chains['action_chains']):
        all_dps.extend(ac)
        for a in ac:
            colors.append(colorsys.hsv_to_rgb(i / len_acs, 0.5, 0.7))

    x_positions = [mf[0] for mf in all_dps]
    y_positions = [mf[1] for mf in all_dps]
    # colors = ['#ff0000' if mf[2] == 1 else '#3366cc' for mf in all_dps]
    """max_milliseconds = max([mf[3] for mf in all_dps])
    if max_milliseconds == 0:
        max_milliseconds = 1

    colors = [
        colorsys.hsv_to_rgb(mf[3] / max_milliseconds, 0.5, 0.7)
        for mf in all_dps
    ]"""

    ax.scatter(x_positions, y_positions, s=10, c=colors, alpha=0.4, label=f'{len_acs} ACs')

    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')

    ax.legend()

    ax.grid(True)
    fig.tight_layout()

    if show:
        plt.show()

    else:
        f = io.BytesIO()
        fig.savefig(f, format='svg')

        f.seek(0)

        return f


def mouse_heatmap():
    """q = User.query_filtered(threshold=200, data_type=DataPointDataType.MOUSE.value)
    print(q.count())"""

    u = User.query_filtered().first()

    action_chains = u.get_mouse_action_chains()

    from pprint import pprint
    print(len(action_chains))
    print(len([ac for ac in action_chains if len(ac) > 10]))

    # user_mouse_heatmap(u)
