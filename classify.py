import argparse

import flwr as fl

from fmexp import create_app
from fmexp.fmclassify import FMClassifier
from fmexp.fmclassify.client import FMFederatedClient


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Classifier Runner')
    parser.add_argument('-c', default='client', required=False, dest='client_or_server', choices=['client', 'server'])
    parser.add_argument('-m', default='request', required=False, dest='mode', choices=['request', 'request_advanced', 'mouse', 'mouse_advanced'])

    args = parser.parse_args()
    client_or_server = args.client_or_server
    mode = args.mode
    if client_or_server == 'client':
        fl.client.start_numpy_client('127.0.0.1:5101', client=FMFederatedClient())

    elif client_or_server == 'server':
        classifier = FMClassifier()
        classifier.load_data(test_only=True)

        strategy = fl.server.strategy.FedAvg(
            min_available_clients=2,
            eval_fn=classifier.get_eval_fn(),
            on_fit_config_fn=lambda rnd: { 'rnd': rnd },
        )
        fl.server.start_server(
            server_address='127.0.0.1:5101',
            strategy=strategy,
            config={ 'num_rounds': 5 },
        )

    else:
        """for n_estimators in [100, 150, 200, 1000]:
            for max_depth in [None, 1, 2, 3]:"""
        for n_estimators in [100]:
            for max_depth in [1]:
                print('n_estimators', n_estimators)
                print('max_depth', max_depth)

                classifier = FMClassifier(n_estimators=n_estimators, max_depth=max_depth)
                classifier.load_data(mode='mouse')
                classifier.train_model()
                score = classifier.test_model()
                print('Score:', score)
                print()
