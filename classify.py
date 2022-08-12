import time
import argparse

import json

# import flwr as fl

from multiprocessing import Process, cpu_count, Queue

from texttable import Texttable
import latextable

from fmexp import create_app
from fmexp.fmclassify import FMClassifier
from fmexp.fmclassify.client import FMFederatedClient


def chunkify(lst, n):
    return [ lst[i::n] for i in range(n) ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Classifier Runner')
    # parser.add_argument('-c', default=None, required=False, dest='client_or_server', choices=['client', 'server'])
    parser.add_argument(
        '-m',
        default='request',
        required=False,
        dest='mode',
        choices=[
            'request',
            'request_advanced',
            'mouse',
            'mouse_advanced',
            'mouse_dataset',
            'test_parameters',
            'data_loader',
            'scenarios',
            'limit',
        ]
    )
    parser.add_argument('-cm', default='mouse', required=False, dest='compare_mode', choices=['request', 'request_advanced', 'mouse', 'mouse_advanced'])
    parser.add_argument('-i', default='fmexp', required=False, dest='instance', choices=['fmexp', 'fmexp2'])
    parser.add_argument('-e', default=5, required=False, dest='epochs')
    # parser.add_argument('-u', default=1, required=False, dest='mouse_user')

    args = parser.parse_args()
    # client_or_server = args.client_or_server
    mode = args.mode
    compare_mode = args.compare_mode
    instance = args.instance
    epochs = int(args.epochs)
    # mouse_user = int(args.mouse_user)

    if mode == 'mouse_dataset':
        print('Training on Mouse')
        classifier = FMClassifier(mode=compare_mode, instance=instance)
        classifier.load_data()
        classifier.train_model()
        score = classifier.test_model()
        print('Score:', score)

        classifier.mode = mode

        # classifier.load_data(test_only=True, cache=True, mouse_users=list(range(1, 22)), cache_instance_name='fmexp')
        classifier.load_data(test_only=True, cache=True, cache_filename='fmexp_cache_mouse_dataset_user1.json')
        score = classifier.test_model()
        print('Score:', score)
        print()

    elif mode == 'data_loader':
        combine_mode = False
        if not combine_mode:
            # for instance in ['fmexp', 'fmexp2']:
            for instance in ['fmexp']:
                for limit in [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, None]:
                    classifier = FMClassifier(mode='mouse_advanced', instance=instance)
                    # classifier = FMClassifier(mode='request', instance='fmexp2')

                    # cache_filename = 'old_bot.json'

                    # cache_filename = 'final_bot_request_new_features.json'
                    # cache_filename = 'final_bot_request_new_features.json'
                    cache_filename = 'final_bot_mouse_limit_{}.json'.format(
                        # instance,
                        limit,
                    )
                    try:
                        classifier.load_data(
                            cache=False,
                            save_cache=True,
                            cache_filename=cache_filename,
                            bot_only=True,
                            limit=limit,
                        )
                    except Exception as e:
                        print('DERP DEPRKLWEOKRNERW', e, limit)
                    # classifier.load_data(cache=False, save_cache=True, cache_filename=cache_filename, human_only=True)

        else:
            """# combine human data from both instances:
            cache_filename = 'final_{}_human_{}.json'
            # for _mode in ['mouse', 'request']:
            for _mode in ['request_new_features']:"""

            for limit in [4, 5, 10, 20, 50, 100, 200, None]:
                cache_filename = 'final_{}_human_mouse_limit_{}.json'

                formatted_filename1 = cache_filename.format('fmexp', limit)
                formatted_filename2 = cache_filename.format('fmexp2', limit)
                print('Loading cache files:', formatted_filename1, formatted_filename2)
                data_total = {
                    'X_train': [],
                    'X_test': [],
                    'y_train': [],
                    'y_test': [],
                }
                for fn in [formatted_filename1, formatted_filename2]:
                    with open(fn, 'r') as f:
                        data = json.loads(f.read())
                        data_total['X_train'].extend(data['X_train'])
                        data_total['X_test'].extend(data['X_test'])
                        data_total['y_train'].extend(data['y_train'])
                        data_total['y_test'].extend(data['y_test'])

                both_fn = 'final_both_human_mouse_limit_{}.json'.format(limit)
                with open(both_fn, 'w') as f:
                    print('Saving to', both_fn)
                    f.write(json.dumps(data_total))

    elif mode == 'test_parameters':
        data_mouse = []
        data_request = []

        param_test_mode = True

        if not param_test_mode:
            max_features_list = ['sqrt']
            n_estimators_list = [1000]
            max_depth_list = [None]

        else:
            max_features_list = [None, 'log2', 'sqrt']
            n_estimators_list = [10, 50, 100, 150, 200, 1000]
            max_depth_list = [None, 1, 2, 3, 4, 5, 10]

            # only max_depth:
            # max_features_list = ['sqrt']
            # n_estimators_list = [50]
            # max_depth_list = list(range(1, 21))

        test_scenarios = []

        for test_mode in [
            #{ 'caption': 'Mouse Data', 'cache_filename': [
            #    'feature_cache/final_bot_mouse_advanced.json',
            #    'feature_cache/final_both_human_mouse.json',
            #] },
            { 'caption': 'Mouse Data', 'cache_filename': [
                'final_both_human_mouse_limit_None.json',
                'final_bot_mouse_limit_None.json',
            ] },
            # { 'caption': 'Request Data', 'cache_filename': [
            #     'old_all.json',
            #] },
            # { 'caption': 'Request Data', 'cache_filename': [
            #    'feature_cache/final_both_request.json',
            #    'feature_cache/final_both_human_request.json',
            #] },
            #{ 'caption': 'Request Data', 'cache_filename': [
            #    'feature_cache/final_bot_request_new_features.json',
            #    'feature_cache/final_both_human_request_new_features.json',
            #] },
        ]:
            for max_features in max_features_list:
                for n_estimators in n_estimators_list:
                    for max_depth in max_depth_list:
                        test_scenarios.append([
                            test_mode,
                            max_features,
                            n_estimators,
                            max_depth,
                        ])

        def run_scenarios(i, n, _scenarios, q):
            this_data = []
            for s in _scenarios:
                test_mode = s[0]
                max_features = s[1]
                n_estimators = s[2]
                max_depth = s[3]
                classifier = FMClassifier(
                    mode='cache_files',
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    max_features=max_features,
                )
                classifier.load_data(
                    cache=True,
                    cache_filename=test_mode['cache_filename'],
                    save_cache=False,
                    bot_human_same_number=True,
                )
                t1 = time.time()
                classifier.train_model()
                t2 = time.time()
                score = classifier.test_model()
                roc_data = classifier.calc_roc_curve()
                precision, recall, f1 = classifier.calc_prf()
                # print('n_estimators', n_estimators)
                # print('max_depth', max_depth)
                # print('Score:', score)
                # print()
                this_data.append([max_features, n_estimators, max_depth, score, precision, recall, f1, roc_data['roc_auc'][1], t2 - t1])

            print(f'[{i}] ', this_data)
            q.put({ 'scenarios': this_data })

        PROCESSES = cpu_count() if len(test_scenarios) >= cpu_count() else len(test_scenarios)

        scenarios_per_proc = chunkify(test_scenarios, PROCESSES)

        processes = []
        mp_queues = []

        for i in range(PROCESSES):
            mp_queue = Queue()
            mp_queues.append(mp_queue)
            this_scenarios = scenarios_per_proc[i]

            p = Process(
                target=run_scenarios,
                args=(i, PROCESSES, this_scenarios, mp_queue, ),
            )
            p.start()
            print(f'[{i}] Started')
            processes.append(p)

        for i, p in enumerate(processes):
            print(f'[{i}] Awaiting result')
            result = mp_queues[i].get()
            for i_s, sc in enumerate(result['scenarios']):
                if 'Mouse' in scenarios_per_proc[i][i_s][0]['caption']:
                    data_mouse.append(sc)
                else:
                    data_request.append(sc)

            print(f'[{i}] Got result')

        for i, p in enumerate(processes):
            p.join()
            print(f'[{i}] Finished')

        print('data_request', data_request)
        print('data_mouse', data_mouse)

        if param_test_mode:
            for i, data in enumerate([data_request, data_mouse]):
                print('DATA:')
                print('-------------------')
                if len(data) == 0:
                    continue
                # from pprint import pprint
                # pprint(data)

                table = Texttable()
                table.set_cols_align(['l' for _ in range(len(data[0]))])
                table.set_cols_valign(['m' for _ in range(len(data[0]))])
                rows =[
                    [
                        'Max Features',
                        '# Estimators',
                        'Max Depth',
                        'Accuracy',
                        'Precision',
                        'Recall',
                        'F1 Score',
                        'AUC',
                        'Training Time',
                    ]
                ]
                # table.add_rows(data[:10])
                rows.extend(sorted(data, key=lambda r: r[3], reverse=True))
                table.add_rows(rows)

                fn = 'table_{}{}.tex'.format('request' if i == 0 else 'mouse', '_param_test' if param_test_mode else '')
                # fn = 'table_{}{}_only_max_depth.tex'.format('request' if i == 0 else 'mouse', '_param_test' if param_test_mode else '')
                print('Writing', fn)

                with open(fn, 'w') as f:
                    f.write(
                        latextable.draw_latex(table)
                    )

    elif mode == 'scenarios':
        data = []

        for sc in [
            {
                'disabled': True,
                'mode': 'request',
                'train_test': [
                    # 'old_bot.json',
                    # 'old_human.json',
                    'old_all.json',
                ],
            },
            {
                'disabled': True,
                'mode': 'request',
                'train_test': [
                    'final_bot_request_new_features.json',
                    'final_both_human_request_new_features.json',
                ],
            },
            {
                'disabled': False,
                'mode': 'mouse_advanced',
                'train_test': [
                    'final_both_human_mouse_limit_None.json',
                    'final_bot_mouse_limit_None.json',
                ],
                'confusion': True,
            },
            {
                'disabled': True,
                'mode': 'mouse',
                'train_test': [
                    'final_both_human_mouse_limit_None.json',
                    # 'feature_cache/final_both_human_mouse.json',
                    'feature_cache/final_bot_mouse.json',
                ],
            },
        ]:
            if sc.get('disabled'):
                continue

            print('SC:', sc)
            sc_mode = sc.get('mode') or mode

            classifier = FMClassifier(
                mode=sc_mode,
                instance=instance,
            )
            classifier.load_data(
                cache=True,
                save_cache=False,
                cache_filename=sc,
                bot_human_same_number=True,
            )
            classifier.train_model()
            score = classifier.test_model()
            t1 = time.time()
            classifier.train_model()
            t2 = time.time()
            score = classifier.test_model()
            roc_data = classifier.calc_roc_curve()
            precision, recall, f1 = classifier.calc_prf()
            data.append([sc['mode'], score, precision, recall, f1, roc_data['roc_auc'][1], t2 - t1])
            print('Score:', score)
            print()

            if sc.get('confusion'):
                tn, fp, fn, tp = classifier.calc_confusion_matrix_values()
                confusion_table = Texttable()
                confusion_table.set_cols_align(['r' for _ in range(3)])
                confusion_table.set_cols_valign(['m' for _ in range(3)])
                confusion_rows = [
                    ['', 'Positive prediction', 'Negative prediction'],
                    ['Positive value', tp, fn],
                    ['Negative value', fp, tn],
                ]
                confusion_table.add_rows(confusion_rows)

                confusion_fn = 'table_confusion_scenarios.tex'
                print('Writing', fn)

                with open(confusion_fn, 'w') as f:
                    f.write(
                        latextable.draw_latex(confusion_table)
                    )

        table = Texttable()
        table.set_cols_align(['l' for _ in range(len(data[0]))])
        table.set_cols_valign(['m' for _ in range(len(data[0]))])
        rows = [
            [
                'Scenario',
                'Accuracy',
                'Precision',
                'Recall',
                'F1 Score',
                'AUC',
                'Training Time',
            ]
        ]
        # table.add_rows(data[:10])
        rows.extend(sorted(data, key=lambda r: r[1], reverse=True))
        table.add_rows(rows)

        fn = 'table_scenarios.tex'
        print('Writing', fn)

        with open(fn, 'w') as f:
            f.write(
                latextable.draw_latex(table)
            )

    elif mode == 'limit':
        data = []
        # limits = [5, 10, 20, 50, 100, None]
        limits = [4, 5, 10, 20, 50, 100, 200, None]

        for limit in limits:
            classifier = FMClassifier(
                mode='mouse_advanced',
            )
            classifier.load_data(
                cache=True,
                cache_filename=[
                    'final_both_human_mouse_limit_{}.json'.format(limit),
                    'final_bot_mouse_limit_{}.json'.format(limit),
                ],
                save_cache=False,
                bot_human_same_number=True,
            )
            t1 = time.time()
            classifier.train_model()
            t2 = time.time()
            score = classifier.test_model()
            roc_data = classifier.calc_roc_curve()
            precision, recall, f1 = classifier.calc_prf()
            # print('n_estimators', n_estimators)
            # print('max_depth', max_depth)
            # print('Score:', score)
            # print()
            print('LIMIT', [limit, score, precision, recall, f1, roc_data['roc_auc'][1], t2 - t1])
            data.append([limit, score, precision, recall, f1, roc_data['roc_auc'][1], t2 - t1])

        table = Texttable()
        table.set_cols_align(['l' for _ in range(len(data[0]))])
        table.set_cols_valign(['m' for _ in range(len(data[0]))])
        rows =[
            [
                'Data Points / Session',
                'Accuracy',
                'Precision',
                'Recall',
                'F1 Score',
                'AUC',
                'Training Time',
            ]
        ]
        # table.add_rows(data[:10])
        rows.extend(sorted(data, key=lambda r: r[1], reverse=True))
        table.add_rows(rows)

        # fn = 'table_{}{}.tex'.format('request' if i == 0 else 'mouse', '_param_test' if param_test_mode else '')
        fn = 'table_limit_mouse.tex'
        print('Writing', fn)

        with open(fn, 'w') as f:
            f.write(
                latextable.draw_latex(table)
            )

    else:
        classifier = FMClassifier(
            mode=mode,
            instance=instance,
        )
        classifier.load_data(
            cache=False,
        )
        classifier.train_model()
        score = classifier.test_model()
        print('Score:', score)
        print()
