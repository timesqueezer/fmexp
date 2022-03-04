import argparse

from fmexp import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from fmexp.fmclassify import FMClassifier
        classifier = FMClassifier()
        classifier.load_data()
        classifier.train_model()
        score = classifier.test_model()
        print(score)
