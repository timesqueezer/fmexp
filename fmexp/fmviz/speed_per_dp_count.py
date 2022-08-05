#!/usr/bin/env python

from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np

from fmexp.extensions import db
from fmexp.fmclassify import FMClassifier
from fmexp.models import (
    User,
    DataPoint,
    DataPointDataType,
)

DATA = [
    [100, 0.027, 0.0077, 93.67],
    [500, 0.19, 0.0089, 94.32],
    [1000, 0.35, 0.0093, 94.28],
    [1500, 0.5, 0.0105, 94.25],
    [2000, 0.9, 0.010, 95.18],
]

def speed_per_dp_count():
    """plt.figure()
    lw = 1.5

    plt.plot(
        roc_data['fpr'][1],
        roc_data['tpr'][1],
        # color="#cc3344",
        lw=lw,
        label='{} {} {}'.format(
            roc_data_list_item['mode'],
            roc_data_list_item['instance'],
            "(area = %0.2f)" % roc_data['roc_auc'][1],
        )
    )
    plt.plot([0, 1], [0, 1], color="grey", lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    # plt.title("Receiver operating characteristic")
    plt.legend(loc="lower right")
    plt.show()"""

    fig, ax_f = plt.subplots()
    ax_c = ax_f.twinx()

    SECONDS_MAX = 1

    def convert_ax_score_to_seconds(ax_score):
        def score_to_seconds(v):
            return (v / 100) * SECONDS_MAX

        y1, y2 = ax_f.get_ylim()
        ax_c.set_ylim(score_to_seconds(y1), score_to_seconds(y2))
        ax_c.figure.canvas.draw()

    ax_f.callbacks.connect("ylim_changed", convert_ax_score_to_seconds)
    ax_f.plot(
        [d[0] for d in DATA],
        [d[1] for d in DATA],
        lw=1.5,
        marker='o',
        label='Total prediction time',
        color='#e996a9',
    )
    ax_f.plot(
        [d[0] for d in DATA],
        [d[2] for d in DATA],
        lw=1.5,
        marker='o',
        label='Prediction time without feature extraction',
        color='#5099EC',
    )
    ax_c.plot(
        [d[0] for d in DATA],
        [d[3] for d in DATA],
        lw=1.5,
        marker='o',
        label='Accuracy',
        color='#97e996',
    )
    ax_f.set_ylim(0.001, 1)
    ax_f.set_yscale('log')
    ax_c.set_ylim(90, 100)
    ax_f.set_xlim(0, 2100)

    # ax_f.set_title('Execution speed and score versus number of previous data points'.title())
    ax_f.set_xlabel('Number of previous data points')
    ax_f.set_ylabel('Seconds')
    ax_c.set_ylabel('Accuracy')


    fig.legend(loc="center", bbox_to_anchor=(0.7, 0.2))

    plt.show()
