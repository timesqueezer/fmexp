#!/usr/bin/env python

import io

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

from fmexp.extensions import db
from fmexp.models import (
    User,
    DataPoint,
    DataPointDataType,
)



def user_mouse_heatmap(user, show=True):
    mouse_features = user.get_mouse_features()
    x_positions = [mf[0] for mf in mouse_features['data']]
    y_positions = [mf[1] for mf in mouse_features['data']]
    colors = ['#ff0000' if mf[2] == 1 else '#3366cc' for mf in mouse_features['data']]

    if show:
        fig, ax = plt.subplots()

    else:
        fig = Figure()
        ax = fig.subplots()

    ax.scatter(x_positions, y_positions, c=colors, alpha=0.2)
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')

    ax.grid(True)
    fig.tight_layout()

    if show:
        plt.show()

    else:
        f = io.BytesIO()
        fig.savefig(f, format='png')

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
