#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

from fmexp.extensions import db
from fmexp.models import (
    User,
    DataPoint,
    DataPointDataType,
)


# NUM_BINS = 50
NUM_BINS = 30


def user_hist(bot=False):
    print('user query', User.query.count())
    print('user query filtered', User.query_filtered().count())

    # filtered_user_uuids = [u.uuid for u in User.query_filtered]

    x_request_data = [r[0] for r in (
        db.session.query(
            db.func.count(DataPoint.id)
        )
        .group_by(DataPoint.user_uuid)
        .having(db.func.count(DataPoint.id) > 2)
        .having(db.func.count(DataPoint.id) < 200)
        .filter(
            DataPoint.data_type == DataPointDataType.REQUEST.value,
            User.query.filter(User.uuid==DataPoint.user_uuid, User.is_bot==bot).exists(),
        )
        .all()
    )]
    max_value_request = max(x_request_data)
    print('max_value_request', max_value_request)

    x_mouse_data = [r[0] for r in (
        db.session.query(
            db.func.count(DataPoint.id)
        )
        .group_by(DataPoint.user_uuid)
        .having(db.func.count(DataPoint.id) > 2)
        .having(db.func.count(DataPoint.id) < 2000)
        .filter(DataPoint.data_type == DataPointDataType.MOUSE.value)
        .all()
    )]
    max_value_mouse = max(x_mouse_data)
    print('max_value_mouse', max_value_mouse)

    # plot:
    fig, (ax1, ax2) = plt.subplots(1, 2)

    fig.tight_layout()

    ax1.hist(x_request_data, bins=NUM_BINS, linewidth=0.5, edgecolor="white")
    ax2.hist(x_mouse_data, bins=NUM_BINS, linewidth=0.5, edgecolor="white")

    """ax1.set(xlim=(0, NUM_BINS), xticks=np.arange(1, NUM_BINS),
           ylim=(0, max_value_request), yticks=np.linspace(0, max_value_request, 9))
    ax2.set(xlim=(0, NUM_BINS), xticks=np.arange(1, NUM_BINS),
           ylim=(0, max_value_mouse), yticks=np.linspace(0, max_value_mouse, 9))"""

    ax1.set_xlabel('# request datapoints')
    ax1.set_ylabel('# users')
    ax2.set_xlabel('# mouse datapoints')
    ax2.set_ylabel('# users')

    plt.show()
