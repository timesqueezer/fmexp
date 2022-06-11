import os
from multiprocessing import Process, cpu_count, Queue

import orjson as json

import numpy as np

import flwr as fl

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

from sklearn.metrics import roc_auc_score, roc_curve, auc

from pprint import pprint


RANDOM_STATE = 42


def chunkify(lst, n):
    return [ lst[i::n] for i in range(n) ]


class FMClassifier:
    def __init__(self, n_estimators=100, max_depth=1):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.set_initial_params()

    def get_model_parameters(self):
        print('GET PARAMS')
        params = {
            'rfc_params': self.clf.get_params(),
            'estimator_params': []
        }

        print('has estimators_', hasattr(self.clf, 'estimators_'))
        if hasattr(self.clf, 'estimators_'):
            for e in self.clf.estimators_:
                params['estimator_params'].append(e.get_params())

        return params

    def set_model_parameters(self, parameters):
        print('SET PARAMS')
        self.clf.set_params(**parameters['rfc_params'])

        print('has estimators_', hasattr(self.clf, 'estimators_'))

        if hasattr(self.clf, 'estimators_'):
            for (e, i) in enumerate(self.clf.estimators_):
                e.set_params(**parameters['estimator_params'][i])

    def set_initial_params(self):
        self.clf = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=RANDOM_STATE,
        )

    """def partition(self, X, y, num_partitions):
        return list(
            zip(np.array_split(X, num_partitions), np.array_split(y, num_partitions))
        )"""

    def get_eval_fn(self):
        def eval_fn(parameters):
            self.set_model_parameters(parameters)
            score = self.test_model()
            return score, { 'accuracy': score }

        return eval_fn

    def load_data(self, mode='request', test_only=False, cache=True):
        from fmexp import create_app
        from fmexp.models import (
            DataPoint,
            User,
            DataPointDataType,
        )

        app = create_app()

        print('loading training data')
        cache_filename = 'fmexp_cache_{}.json'.format(mode)
        if cache and os.path.exists(cache_filename):
            with open(cache_filename, 'r') as f:
                data = json.loads(f.read())
                self.X_train = data['X_train']
                self.X_test = data['X_test']
                self.y_train = data['y_train']
                self.y_test = data['y_test']

        else:
            with app.app_context():
                q = User.query_filtered().order_by(User.email)

                if test_only:
                    q = q.limit(q.count() // 10)

                # get data to not share context between processes
                q = q.all()

            if mode == 'request':
                X = []
                y = []

                with app.app_context():
                    X = [u.get_accumulated_request_features() for u in q]
                    y = [1.0 if u.is_bot else 0.0 for u in q]

            elif mode == 'mouse':
                X = []
                y = []

                def get_user_mouse_features(i, n, user_ids, q):
                    from fmexp import create_app

                    p_app = create_app()
                    with p_app.app_context():
                        p_X = []
                        p_y = []

                        for u in User.query.filter(User.uuid.in_(user_ids)):
                            mouse_features = u.get_mouse_features()
                            p_X.extend([ac_features for ac_features in mouse_features])
                            p_y.extend([1.0 if u.is_bot else 0.0 for _ in range(len(mouse_features))])

                        q.put({ 'X': p_X, 'y': p_y })

                PROCESSES = cpu_count() * 2

                all_user_ids = [u.uuid for u in q]
                user_ids_per_proc = chunkify(all_user_ids, PROCESSES)

                processes = []
                mp_queues = []

                for i in range(PROCESSES):
                    mp_queue = Queue()
                    mp_queues.append(mp_queue)
                    user_ids = user_ids_per_proc[i]

                    p = Process(
                        target=get_user_mouse_features,
                        args=(i, PROCESSES, user_ids, mp_queue, ),
                    )
                    p.start()
                    print(f'[{i}] Started')
                    processes.append(p)

                for i, p in enumerate(processes):
                    print(f'[{i}] Awaiting result')
                    result = mp_queues[i].get()
                    X.extend(result['X'])
                    y.extend(result['y'])
                    print(f'[{i}] Got result')

                for i, p in enumerate(processes):
                    p.join()
                    print(f'[{i}] Finished')

            if test_only:
                self.X_test, self.y_test = X, y

            else:
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    X, y, test_size=0.1, random_state=RANDOM_STATE
                )

                if cache:
                    with open(cache_filename, 'w') as f:
                        data = {
                            'X_train': self.X_train,
                            'X_test': self.X_test,
                            'y_train': self.y_train,
                            'y_test': self.y_test,
                        }
                        f.write(json.dumps(data))

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
