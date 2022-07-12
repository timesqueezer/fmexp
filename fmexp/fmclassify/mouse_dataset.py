import os
import csv

from multiprocessing import Process, cpu_count, Queue

import numpy as np


def chunkify(lst, n):
    return [ lst[i::n] for i in range(n) ]


def extract_mouse_features(mouse_ac_data):
    MIN_ACTIONS = 4
    ac_features = []

    ac_length = len(mouse_ac_data['action_chains'])

    for aci, ac in enumerate(mouse_ac_data['action_chains']):
        if len(ac) < MIN_ACTIONS:
            continue

        x = np.array([a[0] for a in ac])
        y = np.array([a[1] for a in ac])
        t = np.array([a[3] for a in ac])

        # first phase: preprocessing

        # distance to start
        s = np.array([
            sum(
                np.sqrt(
                    ((x[k + 1] - x[k]) ** 2) +
                    ((y[k + 1] - y[k]) ** 2)
                )
                for k in range(i)
            ) for i, _ in enumerate(x)
        ])

        # TODO: linear + cubic spline interpolation
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html

        axis_points = np.arange(0, max(t), 20)

        x_lin_interp = np.interp(axis_points, t, x)
        y_lin_interp = np.interp(axis_points, t, y)

        # cs_x = CubicSpline(t, x)
        # cs_y = CubicSpline(t, y)

        # spatial information
        x_prime = x_lin_interp
        y_prime = y_lin_interp

        # x_prime = cs_x(axis_points)
        # y_prime = cs_y(axis_points)
        # print(f'{aci}/{ac_length}', len(ac), len(x_prime), max(t))

        s_prime = np.array([
            sum(
                np.sqrt(
                    ((x_prime[k + 1] - x_prime[k]) ** 2) +
                    ((y_prime[k + 1] - y_prime[k]) ** 2)
                )
                for k in range(i)
            ) for i in range(len(x_prime))
        ])

        theta = [0]
        theta.extend([
            np.arctan2(
                (y_prime[k + 1] - y_prime[k]),
                (x_prime[k + 1] - x_prime[k])
            )
            for k in range(len(y_prime) - 1)
        ])

        # print(2)

        # todo: curvature and maybe use equation from paper

        """fig, ax = plt.subplots()
        # ax.plot(t, x, 'o', label='x')
        # ax.plot(t, y, 'o', label='y')
        # ax.plot(t, s, label='s')
        # ax.plot(axis_points, x_lin_interp, label='x lin interp')
        # ax.plot(axis_points, y_lin_interp, label='y lin interp')
        # ax.plot(axis_points, cs_x(axis_points), label='x cubic interp')
        # ax.plot(axis_points, cs_y(axis_points), label='y interp')


        # ax.plot(axis_points, x_prime, label='x\'')
        # ax.plot(axis_points, y_prime, label='y\'')
        ax.plot(axis_points, theta, label='theta')

        ax.legend()
        plt.show()"""

        # temporal information
        # dt = k / len(x)
        len_x = len(x)

        v_x = [0]
        v_x.extend([
            (x[k] - x[k - 1]) / (k / len_x)
            for k in range(1, len_x)
        ])

        v_y = [0]
        v_y.extend([
            (y[k] - y[k - 1]) / (k / len_x)
            for k in range(1, len(y))
        ])

        v = [
            np.sqrt(v_x[k]**2 + v_y[k]**2)
            for k in range(len(v_x))
        ]

        # acceleration
        a = [0]
        a.extend([
            (v[k] - v[k - 1]) / (k / len_x)
            for k in range(1, len(v))
        ])

        # jerk
        j = [0]
        j.extend([
            (a[k] - a[k - 1]) / (k / len_x)
            for k in range(1, len(a))
        ])

        # angular velocity
        w = [0]
        w.extend([
            theta[k] - theta[k - 1] / (k / len_x)
            for k in range(1, len(theta))
        ])

        # statistical analysis for actual feature data
        features = []

        """for _v in vector:
            for measure in minimum, maximum, mean, standard deviation, and (maximum - minimum)."""

        # for vector in [x_prime, y_prime, theta, curvature, delta_curvature, v_x, v_y, v, a, j, w]
        for vector in [x_prime, y_prime, theta, v_x, v_y, v, a, j, w]:
            for measure in [np.min, np.max, np.mean, np.std, 'max-min']:
                if measure == 'max-min':
                    features.append(np.max(vector) - np.min(vector))

                else:
                    features.append(measure(vector))

        # t_n: time of stroke
        # s_n-1: length of stroke
        t_n = t[-1] - t[0]
        s_n_1 = s[-1]

        features.append(t_n)
        features.append(s_n_1)

        # straightness
        straightness = np.sqrt(
            ( (x[0] - x[-1]) ** 2 ) +
            ( (y[0] - y[-1]) ** 2 )
        ) / max(s_n_1, 1)

        features.append(straightness)

        # jitter: ratio between original and smoothed path lengths
        jitter = s[-1] / max(s_prime[-1], 1)

        features.append(jitter)

        # TODO: number of "critical points" which have high curvature
        # TODO: time to click
        # TODO: number of pauses
        # TODO: paused time
        # TODO: paused time ratio

        ac_features.append(features)

    return ac_features


def get_mouse_dataset_data(mouse_users=[]):
    def get_mouse_features_from_csv(proc_num, n, filepaths, q):
        ACTION_MAX_LENGTH = 2 # seconds
        ACTION_MAX_NUM = 50

        p_X = []
        p_y = []

        for filepath in filepaths:
            print(f'[{proc_num}] Loading', filepath)
            with open(filepath) as csvfile:
                reader = csv.DictReader(csvfile)
                action_chains = []

                current_chain = []
                first_td = None
                counter = 0
                next_row = None
                time_to_next = 0

                # for row in list(reader)[:500]:
                try:
                    rows = list(reader)
                    for i, row in enumerate(rows):
                        td = 0
                        counter += 1

                        x = int(row['x'])
                        y = int(row['y'])
                        dp_type = 0 if row['state'] == 'Move' else 1
                        timestamp = int(row['client timestamp'])

                        if not first_td:
                            first_td = timestamp

                        td = timestamp - first_td

                        dp_data = (
                            x,
                            y,
                            dp_type,
                            td,
                        )

                        current_chain.append(dp_data)

                        if i < (len(rows) - 1):
                            next_row = rows[i + 1]
                            time_to_next = int(next_row['client timestamp']) - timestamp

                        if dp_type != 0 or \
                            time_to_next > (ACTION_MAX_LENGTH * 1000) or \
                            counter >= ACTION_MAX_NUM:
                            action_chains.append(current_chain)
                            current_chain = []
                            first_td = None
                            counter = 0
                            time_to_next = 0

                    mouse_features = extract_mouse_features({ 'action_chains': action_chains })
                    p_X.extend([ac_features for ac_features in mouse_features])
                    p_y.extend([0.0 for _ in range(len(mouse_features))])

                except Exception as e:
                    print(f'[{proc_num}] DERP', filepath, e)

        q.put({ 'X': p_X, 'y': p_y })

    PROCESSES = cpu_count()
    # PROCESSES = 1

    all_filepaths = []

    # for i in range(1, 22):
    # mouse_user = mouse_user or 2
    # range_start = mouse_user
    # range_end = mouse_user + 1

    for i in mouse_users:
        folder_path = f'datasets/dfl_mouse_data/User{i}'
        print('Loading', folder_path)

        for filename in os.listdir(folder_path):
            all_filepaths.append(
                os.path.join(folder_path, filename)
            )

    filepaths_per_proc = chunkify(all_filepaths, PROCESSES)

    processes = []
    mp_queues = []

    X = []
    y = []

    for i in range(PROCESSES):
        mp_queue = Queue()
        mp_queues.append(mp_queue)

        p = Process(
            target=get_mouse_features_from_csv,
            args=(i, PROCESSES, filepaths_per_proc[i], mp_queue, ),
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

    return X, y
