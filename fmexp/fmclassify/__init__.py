import os
from multiprocessing import Process, cpu_count, Queue

import orjson as json

import numpy as np
import flwr as fl
import pandas as pd
import tensorflow as tf

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

from sklearn.metrics import roc_auc_score, roc_curve, auc

from pprint import pprint

from fmexp.fmclassify.mouse_dataset import get_mouse_dataset_data


RANDOM_STATE = 42


def chunkify(lst, n):
    return [ lst[i::n] for i in range(n) ]


class FMClassifier:
    def __init__(self, instance='fmexp', mode='request', n_estimators=100, max_depth=1):
        self.n_estimators = n_estimators
        self.max_depth = max_depth

        self.clf_mode = 'random_forest'
        self.instance = instance
        self.mode = mode
        self.batch_size = 2

        self.set_initial_params()

    def set_initial_params(self):
        if self.clf_mode == 'random_forest':
            self.clf = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=RANDOM_STATE,
            )

        else:
            layers = [
                tf.keras.layers.InputLayer(input_shape=(len(self.get_labels()), )),
            ]

            if 'request' in self.mode:
                layers.extend([
                    tf.keras.layers.Dense(10, kernel_initializer='zeros'),
                    tf.keras.layers.Dense(10, kernel_initializer='zeros'),
                    tf.keras.layers.Dense(2, kernel_initializer='zeros'),
                    tf.keras.layers.Softmax(),
                ])

            elif 'mouse' in self.mode:
                layers.extend([
                    tf.keras.layers.Dense(10, kernel_initializer='zeros'),
                    tf.keras.layers.Dense(10, kernel_initializer='zeros'),
                    tf.keras.layers.Dense(2, kernel_initializer='zeros'),
                    tf.keras.layers.Softmax(),
                ])

            self.clf = tf.keras.models.Sequential(layers)
            self.clf.compile(
                optimizer=tf.keras.optimizers.SGD(learning_rate=1.0),
                # loss=tf.keras.losses.MeanSquaredError(),
                loss=tf.keras.losses.SparseCategoricalCrossentropy(),
            )

    def get_eval_fn(self):
        def eval_fn(parameters):
            self.set_model_parameters(parameters)
            score = self.test_model()
            return score, { 'accuracy': score }

        return eval_fn

    def get_labels(self):
        if 'request' in self.mode:
            return [
                '% HTTP 400 Requests',
                '% CSS Requests',
                '% JS Requests',
                '% Requests with previously requested URL as part of URL',
                'Time between first and last request of session',
            ]

        elif 'mouse' in self.mode:
            labels = []

            for vector in ['x_prime', 'y_prime', 'theta', 'v_x', 'v_y', 'v', 'a', 'j', 'w']:
                for measure in ['min', 'max', 'mean', 'std', 'max-min']:
                    labels.append('{} {}'.format(vector, measure))

            labels.append('t_n time of stroke')
            labels.append('s_n-1 length of stroke')
            labels.append('straightness')
            labels.append('jitter')

            return labels

    def load_data(self, test_only=False, cache=True, mouse_users=[], cache_instance_name=None, cache_filename=None):
        print('loading training data, test_only={}, cache={}'.format(test_only, cache))

        cache_filename = cache_filename or '{}_cache_{}{}.json'.format(
            cache_instance_name or self.instance,
            self.mode,
            ('{}_users'.format(str(len(mouse_users)))) if self.mode == 'mouse_dataset' and mouse_users else ''
        )
        if cache and os.path.exists(cache_filename):
            print('Loading from cache file:', cache_filename)
            with open(cache_filename, 'r') as f:
                data = json.loads(f.read())
                self.X_train = data['X_train']
                self.X_test = data['X_test']
                self.y_train = data['y_train']
                self.y_test = data['y_test']

        else:
            if self.mode == 'mouse_dataset':
                X, y = get_mouse_dataset_data(mouse_users=mouse_users)

            else:
                from fmexp import create_app
                from fmexp.models import (
                    DataPoint,
                    User,
                    DataPointDataType,
                )

                additional_config = None
                if self.instance == 'fmexp2':
                    additional_config = 'fmexp.config2'

                app = create_app(additional_config=additional_config)

                with app.app_context():
                    q = User.query_filtered().order_by(User.email)

                    if test_only:
                        q = q.limit(q.count() // 10)

                    # get data to not share context between processes
                    q = q.all()

                if 'request' in self.mode:
                    X = []
                    y = []

                    with app.app_context():
                        X = [u.get_accumulated_request_features() for u in q]
                        y = [1.0 if u.is_bot else 0.0 for u in q]

                elif 'mouse' in self.mode:
                    X = []
                    y = []

                    def get_user_mouse_features(i, n, user_ids, q, instance):
                        from fmexp import create_app

                        additional_config = None
                        if instance == 'fmexp2':
                            additional_config = 'fmexp.config2'

                        p_app = create_app(additional_config)
                        with p_app.app_context():
                            p_X = []
                            p_y = []

                            for u in User.query.filter(User.uuid.in_(user_ids)):
                                mouse_features = u.get_mouse_features()
                                p_X.extend([ac_features for ac_features in mouse_features])
                                p_y.extend([1.0 if u.is_bot else 0.0 for _ in range(len(mouse_features))])

                            q.put({ 'X': p_X, 'y': p_y })

                    PROCESSES = cpu_count()

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
                            args=(i, PROCESSES, user_ids, mp_queue, self.instance, ),
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
                self.X_train, self.y_train = [], []

            else:
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    X, y, test_size=0.1, random_state=RANDOM_STATE
                )

            if cache:
                with open(cache_filename, 'wb') as f:
                    data = {
                        'X_train': self.X_train,
                        'X_test': self.X_test,
                        'y_train': self.y_train,
                        'y_test': self.y_test,
                    }
                    f.write(json.dumps(data, option=json.OPT_SERIALIZE_NUMPY))

        num_train_total = len(self.y_train)
        num_bots_train = len([y for y in self.y_train if y == 1.0])
        num_humans_train = num_train_total - num_bots_train

        num_test_total = len(self.y_test)
        num_bots_test = len([y for y in self.y_test if y == 1.0])
        num_humans_test = num_test_total - num_bots_test

        print('Loaded Data. Bots: {}/{}, Humans: {}/{}'.format(
            num_bots_train,
            num_bots_test,
            num_humans_train,
            num_humans_test,
        ))

    def train_model(self, epochs=1):
        print('start training model')

        if self.clf_mode == 'random_forest':
            self.clf.fit(
                self.X_train,
                self.y_train,
            )

        else:
            self.clf.fit(
                self.X_train,
                self.y_train,
                epochs=epochs,
                batch_size=self.batch_size,
            )

    def test_model(self):
        if self.clf_mode == 'random_forest':
            return self.clf.score(
                self.X_test,
                self.y_test,
            )

        else:
            return self.clf.evaluate(
                self.X_test,
                self.y_test,
                batch_size=self.batch_size,
                return_dict=True,
            )

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
