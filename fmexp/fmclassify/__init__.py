import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

from sklearn.metrics import roc_auc_score, roc_curve, auc

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
            X, y, test_size=0.5, random_state=42
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

    def get_roc_auc_score(self):
        y_score = self.clf.predict_proba(self.X_test)[:, 1]
        return roc_auc_score(self.y_test, y_score)

    def calc_roc_curve(self):
        y_score = self.clf.predict_proba(self.X_test)

        y_test = np.array([(1 - i, i) for i in self.y_test])

        n_classes = 2

        # Compute ROC curve and ROC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(n_classes):
            fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        return {
            'fpr': fpr,
            'tpr': tpr,
            'roc_auc': roc_auc,
        }
