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


def roc_curves(modes=[], instances=[]):
    roc_data_list = []

    for mode in modes:
        for instance in instances:
            args = {}
            if mode:
                args['mode'] = mode

            if instance:
                args['instance'] = instance

            classifier = FMClassifier(**args)
            classifier.load_data()
            classifier.train_model()
            score = classifier.test_model()
            print('Test Score:', score)
            # print('ROC AUC Score:', classifier.get_roc_auc_score())
            roc_data = classifier.calc_roc_curve()
            roc_data_list.append({
                'mode': mode,
                'instance': instance,
                'roc_data': roc_data,
            })

    plt.figure()
    lw = 1.5

    for roc_data_list_item in roc_data_list:
        roc_data = roc_data_list_item['roc_data']

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
    plt.show()
