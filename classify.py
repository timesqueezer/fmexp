import argparse

import flwr as fl

from fmexp import create_app
from fmexp.fmclassify import FMClassifier
from fmexp.fmclassify.client import FMFederatedClient


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Classifier Runner')
    # parser.add_argument('-c', default=None, required=False, dest='client_or_server', choices=['client', 'server'])
    parser.add_argument('-m', default='request', required=False, dest='mode', choices=['request', 'request_advanced', 'mouse', 'mouse_advanced', 'mouse_dataset'])
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

    else:
        classifier = FMClassifier(mode=mode, instance=instance)
        classifier.load_data(cache=False)
        classifier.train_model()
        score = classifier.test_model()
        print('Score:', score)
