from fmexp.models import (
    User,
    DataPoint,
    DataPointDataType,
    DataPointUserType,
)
from fmexp.utils import fast_query_count


def get_stats():
    stats = []

    stats.append({
        'name': 'Users',
        'count_human': fast_query_count(User.query.filter(User.is_bot == False)),
        'count_bot': fast_query_count(User.query.filter(User.is_bot == True)),
    })

    stats.append({
        'name': 'Request DataPoints',
        'count_human': fast_query_count(
            DataPoint.query.filter(
                DataPoint.data_type == DataPointDataType.REQUEST.value,
                DataPoint.user_type == DataPointUserType.HUMAN.value,
            )
        ),
        'count_bot': fast_query_count(
            DataPoint.query.filter(
                DataPoint.data_type == DataPointDataType.REQUEST.value,
                DataPoint.user_type == DataPointUserType.BOT.value,
            )
        ),
    })

    stats.append({
        'name': 'Mouse DataPoints',
        'count_human': fast_query_count(
            DataPoint.query.filter(
                DataPoint.data_type == DataPointDataType.MOUSE.value,
                DataPoint.user_type == DataPointUserType.HUMAN.value,
            )
        ),
        'count_bot': fast_query_count(
            DataPoint.query.filter(
                DataPoint.data_type == DataPointDataType.MOUSE.value,
                DataPoint.user_type == DataPointUserType.BOT.value,
            )
        ),
    })

    return stats
