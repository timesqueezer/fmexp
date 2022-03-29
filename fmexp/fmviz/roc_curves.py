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


def roc_curves():
    classifier = FMClassifier()
    classifier.load_data()
    classifier.train_model()
    score = classifier.test_model()
    print('Test Score:', score)
    # print('ROC AUC Score:', classifier.get_roc_auc_score())
    roc_data = classifier.calc_roc_curve()

    plt.figure()
    lw = 2
    plt.plot(
        roc_data['fpr'][1],
        roc_data['tpr'][1],
        color="darkorange",
        lw=lw,
        label="ROC curve (area = %0.2f)" % roc_data['roc_auc'][1],
    )
    plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver operating characteristic")
    plt.legend(loc="lower right")
    plt.show()
