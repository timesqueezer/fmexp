import os
import time

from multiprocessing import Process, cpu_count, Queue

import orjson as json

import numpy as np
# import flwr as fl
# import pandas as pd
# import tensorflow as tf

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
    auc,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from pprint import pprint

from fmexp.fmclassify.mouse_dataset import get_mouse_dataset_data

RANDOM_STATE = 2270717344


def chunkify(lst, n):
    return [ lst[i::n] for i in range(n) ]


class FMClassifier:
    def __init__(
        self,
        instance='fmexp',
        mode='request',
        n_estimators=False,
        max_depth=False,
        max_features=False,
        random_state=None,
    ):
        if n_estimators is False:
            self.n_estimators = 100 if 'request' in mode else 200
        else:
            self.n_estimators = n_estimators

        if max_depth is False:
            self.max_depth = None
        else:
            self.max_depth = max_depth

        if max_features is False:
            self.max_features = None if 'request' in mode else 'sqrt'
        else:
            self.max_features = max_features

        self.clf_mode = 'random_forest'
        self.instance = instance
        self.mode = mode
        # self.batch_size = 2
        self.random_state = random_state

        self.set_initial_params()

    def set_initial_params(self):
        if self.clf_mode == 'random_forest':
            self.clf = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                max_features=self.max_features,
                random_state=self.random_state or RANDOM_STATE,
                n_jobs=-1,
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

    def load_data(
        self,
        test_only=False,
        cache=True,
        save_cache=False,
        mouse_users=[],
        cache_instance_name=None,
        cache_filename=None,
        bot_only=False,
        human_only=False,
        live_bot_only=False,
        bot_human_same_number=False,
        limit=None,
        save_test_only=False,
    ):
        print('loading training data, test_only={}, cache={}'.format(test_only, cache))

        cache_filename = cache_filename or '{}_cache_{}{}.json'.format(
            cache_instance_name or self.instance,
            self.mode,
            ('{}_users'.format(str(len(mouse_users)))) if self.mode == 'mouse_dataset' and mouse_users else ''
        )
        if cache:
            self.X_train = []
            self.X_test = []
            self.y_train = []
            self.y_test = []

            if type(cache_filename) == list:
                for i, cf in enumerate(cache_filename):
                    print('Loading from cache file:', i, cf)
                    with open(cf, 'r') as f:
                        data = json.loads(f.read())
                        self.X_train.extend(data['X_train'])
                        self.X_test.extend(data['X_test'])
                        self.y_train.extend(data['y_train'])
                        self.y_test.extend(data['y_test'])

            elif type(cache_filename) == dict:
                if 'train_test' in cache_filename.keys():
                    filenames = []
                    cache_train_test = cache_filename['train_test']
                    if type(cache_train_test) == str:
                        filenames.append(cache_train_test)
                    else:
                        filenames.extend(cache_train_test)

                    for i, cf in enumerate(filenames):
                        print('Loading train + test data from cache file:', i, cf)
                        with open(cf, 'r') as f:
                            data = json.loads(f.read())
                            self.X_train.extend(data['X_train'])
                            self.X_test.extend(data['X_test'])
                            self.y_train.extend(data['y_train'])
                            self.y_test.extend(data['y_test'])

                if 'train' in cache_filename.keys():
                    cache_train = cache_filename['train']

                    cache_train_filenames = []
                    if type(cache_train) == str:
                        cache_train_filenames.append(cache_train)
                    else:
                        cache_train_filenames.extend(cache_train)

                    for i, cf in enumerate(cache_train_filenames):
                        print('Loading training data from cache file:', i, cf)
                        with open(cf, 'r') as f:
                            data = json.loads(f.read())
                            self.X_train.extend(data['X_train'])
                            self.X_train.extend(data['X_test'])
                            self.y_train.extend(data['y_train'])
                            self.y_train.extend(data['y_test'])

                if 'test' in cache_filename.keys():
                    cache_test = cache_filename['test']

                    cache_test_filenames = []

                    if type(cache_test) == str:
                        cache_test_filenames.append(cache_test)
                    else:
                        cache_test_filenames.extend(cache_test)


                    for i, cf in enumerate(cache_test_filenames):
                        print('Loading testing data from cache file:', i, cf)
                        with open(cf, 'r') as f:
                            data = json.loads(f.read())
                            self.X_test.extend(data['X_train'])
                            self.X_test.extend(data['X_test'])
                            self.y_test.extend(data['y_train'])
                            self.y_test.extend(data['y_test'])

            elif os.path.exists(cache_filename):
                print('Loading from cache file:', cache_filename)
                with open(cache_filename, 'r') as f:
                    data = json.loads(f.read())
                    self.X_train = data['X_train']
                    self.X_test = data['X_test']
                    self.y_train = data['y_train']
                    self.y_test = data['y_test']

            else:
                print('Invalid cache parameters')

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
                    q = User.query_filtered(reverse_threshold=live_bot_only).order_by(User.email)

                    if bot_only:
                        q = q.filter(User.is_bot == True)

                    elif human_only:
                        q = q.filter(User.is_bot == False)

                    if test_only:
                        q = q.limit(q.count() // 10)

                    # get data to not share context between processes
                    q = q.all()

                if 'request' in self.mode:
                    X = []
                    y = []

                    with app.app_context():
                        args = {}
                        if limit:
                            args['limit'] = limit

                        X = [u.get_accumulated_request_features(**args) for u in q]
                        y = [1.0 if u.is_bot or live_bot_only else 0.0 for u in q]

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

                            args = {}
                            if limit:
                                args['limit'] = limit

                            for u in User.query.filter(User.uuid.in_(user_ids)):
                                mouse_features = u.get_mouse_features(**args)
                                p_X.extend([ac_features for ac_features in mouse_features])
                                p_y.extend([1.0 if u.is_bot or live_bot_only else 0.0 for _ in range(len(mouse_features))])

                            q.put({ 'X': p_X, 'y': p_y })

                    PROCESSES = cpu_count()

                    all_user_ids = [
                        u.uuid for u in q
                        if live_bot_only or not u.is_bot
                        or (u.bot_mouse_mode == 'advanced_random_delays' and self.mode == 'mouse_advanced')
                        or (u.bot_mouse_mode != 'advanced_random_delays' and self.mode != 'mouse_advanced')
                    ]
                    print('all_user_ids', len(all_user_ids))
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

            if test_only or save_test_only:
                self.X_test, self.y_test = X, y
                self.X_train, self.y_train = [], []

            else:
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    X, y, test_size=0.1, random_state=self.random_state or RANDOM_STATE
                )
                print('LENGTHS AFTER SPLIT:')
                print('y_train', len(self.y_train))
                print('y_test', len(self.y_test))
                print('X_train', len(self.X_train))
                print('X_test', len(self.X_test))

            if save_cache:
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
        num_humans_train_wtf = len([y for y in self.y_train if y == 0.0])
        # num_humans_train = len([y for y in self.y_train if y == 0.0])

        num_test_total = len(self.y_test)
        num_bots_test = len([y for y in self.y_test if y == 1.0])
        num_humans_test = num_test_total - num_bots_test
        num_humans_test_wtf = len([y for y in self.y_test if y == 0.0])

        if bot_human_same_number:
            if num_bots_train > num_humans_train:
                bots_y_train = [y for y in self.y_train if y == 1.0][:num_humans_train]
                bots_X_train = [X for i, X in enumerate(self.X_train) if self.y_train[i] == 1.0][:num_humans_train]

                humans_y_train = [y for y in self.y_train if y == 0.0]
                humans_X_train = [X for i, X in enumerate(self.X_train) if self.y_train[i] == 0.0]
                self.y_train = [*bots_y_train, *humans_y_train]
                self.X_train = [*bots_X_train, *humans_X_train]

                num_bots_train = len(bots_y_train)
                num_humans_train = len(humans_y_train)
                num_train_total = len(self.y_train)

            if num_bots_test > num_humans_test:
                bots_y_test = [y for y in self.y_test if y == 1.0][:num_humans_test]
                bots_X_test = [X for i, X in enumerate(self.X_test) if self.y_test[i] == 1.0][:num_humans_test]

                humans_y_test = [y for y in self.y_test if y == 0.0]
                humans_X_test = [X for i, X in enumerate(self.X_test) if self.y_test[i] == 0.0]
                self.y_test = [*bots_y_test, *humans_y_test]
                self.X_test = [*bots_X_test, *humans_X_test]

                num_bots_test = len(bots_y_test)
                num_humans_test = len(humans_y_test)
                num_test_total = len(self.y_test)

        # print('CHECKECKEKC 2', self.X_train[0:20])
        print('Loaded Data. Bots: {}/{} ({} total), Humans: {}/{} ({} total)'.format(
            num_bots_train,
            num_bots_test,
            num_bots_train + num_bots_test,
            num_humans_train,
            num_humans_test,
            num_humans_train + num_humans_test,
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
        X = None

        if 'request' in self.mode:
            X = np.reshape(
                user.get_accumulated_request_features(),
                (1, -1)
            )

        elif 'mouse' in self.mode:
            X = [ac_features for ac_features in user.get_mouse_features()]
            if (len(X) == 0):
                return [-1]

        t1 = time.time()
        score = self.clf.predict(X)
        t2 = time.time()
        print('P time:', t2 - t1)
        return score

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
        fpr['micro'], tpr['micro'], _ = roc_curve(y_test.ravel(), y_score.ravel())
        roc_auc['micro'] = auc(fpr['micro'], tpr['micro'])

        return {
            'fpr': fpr,
            'tpr': tpr,
            'roc_auc': roc_auc,
        }

    def calc_prf(self):
        y_score = [round(i) for i in list(self.clf.predict_proba(self.X_test)[:, 1])]
        # print('self.y_test', [m for m in self.y_test if type(m) != float])
        # print('y_score', [m for m in y_score if type(m) != float])
        y_test = [round(i) for i in self.y_test]
        precision = precision_score(
            y_test,
            y_score,
        )
        recall = recall_score(
            y_test,
            y_score,
        )
        f1 = f1_score(
            y_test,
            y_score,
        )

        return precision, recall, f1

    def calc_confusion_matrix_values(self):
        y_score = [round(i) for i in list(self.clf.predict_proba(self.X_test)[:, 1])]
        y_test = [round(i) for i in self.y_test]

        return confusion_matrix(y_test, y_score).ravel()
