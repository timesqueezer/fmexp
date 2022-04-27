import argparse

from fmexp import create_app

if __name__ == '__main__':
    """app = create_app()
    with app.app_context():"""
    if True:
        from fmexp.fmclassify import FMClassifier

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
