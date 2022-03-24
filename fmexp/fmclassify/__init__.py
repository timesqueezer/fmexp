import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

from pprint import pprint


class FMClassifier:
    def __init__(self):
        self.clf = RandomForestClassifier(max_depth=1, random_state=0)

    def load_data(self):
        from fmexp.models import (
            DataPoint,
            User,
            DataPointDataType,
        )

        print('loading training data')

        # vec = DictVectorizer()

        q = User.query_filtered()

        X = [u.get_accumulated_request_features() for u in q]
        y = [1.0 if u.is_bot else 0.0 for u in q]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.1, random_state=42
        )

    def train_model(self):
        print('start training model')

        self.clf.fit(self.X_train, self.y_train)

    def test_model(self):
        return self.clf.score(self.X_test, self.y_test)

    def predict(self, user):
        X = np.reshape(
            user.get_accumulated_request_features(),
            (1, -1)
        )
        return self.clf.predict(X)
