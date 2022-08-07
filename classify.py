import argparse

import json

# import flwr as fl

from texttable import Texttable
import latextable

from fmexp import create_app
from fmexp.fmclassify import FMClassifier
from fmexp.fmclassify.client import FMFederatedClient


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
        cache_filename = f'final_bot_mouse.json'
        classifier = FMClassifier(mode='mouse', instance='fmexp')
        classifier.load_data(cache=True, cache_filename=cache_filename, bot_only=True)

        # combine human data from both instances:
        """cache_filename = 'final_{}_human_{}.json'
        for _mode in ['mouse', 'request']:
            formatted_filename1 = cache_filename.format('fmexp1', _mode)
            formatted_filename2 = cache_filename.format('fmexp2', _mode)
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

            both_fn = 'final_both_human_{}.json'.format(_mode)
            with open(both_fn, 'w') as f:
                print('Saving to', both_fn)
                f.write(json.dumps(data_total))"""

    elif mode == 'test_parameters':
        data = []
        if False:
            max_features_list = ['sqrt']
            n_estimators_list = [100]
            max_depth_list = [None]

        else:
            max_features_list = [None, 'log2', 'sqrt']
            n_estimators_list = [10, 50, 100, 150, 200, 1000]
            max_depth_list = [None, 1, 2, 3, 4]

        for test_mode in [
            { 'caption': 'Mouse Data', 'cache_filename': [
                'feature_cache/final_both_human_mouse.json',
                'feature_cache/final_bot_mouse_advanced.json',
            ] },
            { 'caption': 'Request Data', 'cache_filename': [
                'feature_cache/final_both_human_request.json',
                'feature_cache/final_bot_request.json',
            ] },
        ]:
            for max_features in max_features_list:
                for n_estimators in n_estimators_list:
                    for max_depth in max_depth_list:
                        classifier = FMClassifier(
                            mode='cache_files',
                            n_estimators=n_estimators,
                            max_depth=max_depth,
                            max_features=max_features,
                        )
                        classifier.load_data(
                            cache=True,
                            cache_filename=test_mode['cache_filename'],
                        )
                        classifier.train_model()
                        score = classifier.test_model()
                        roc_data = classifier.calc_roc_curve()
                        precision, recall, f1 = classifier.calc_prf()
                        # print('n_estimators', n_estimators)
                        # print('max_depth', max_depth)
                        # print('Score:', score)
                        # print()
                        data.append([max_features, n_estimators, max_depth, score, precision, recall, f1, roc_data['roc_auc']])

        print('DATA:')
        print('-------------------')
        # from pprint import pprint
        # pprint(data)

        table = Texttable()
        table.set_cols_align(['l' for _ in range(len(data[0]))])
        table.set_cols_valign(['m' for _ in range(len(data[0]))])
        table.add_rows([['Max Features', '# Estimators', 'Max Depth', 'Score', 'Precision', 'Recall', 'F1 Score', 'AUC']])
        table.add_rows(data[:10])

        fn = 'table_.tex'.format(test_mode['caption'].lower().replace(' ', '_'))
        print('Writing', fn)

        with open(fn, 'w') as f:
            f.write(
                latextable.draw_latex(table, caption=test_mode['caption'])
            )


    else:
        classifier = FMClassifier(mode=mode, instance=instance)
        classifier.load_data(cache=False)
        classifier.train_model()
        score = classifier.test_model()
        print('Score:', score)
