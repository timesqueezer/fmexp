import argparse

# from fmexp import create_app
from fmexp.fmclassify import FMClassifier


if __name__ == '__main__':
    classifier = FMClassifier(mode='mouse_dataset')
    classifier.load_data(test_only=True, cache=True, mouse_users=list(range(1, 22)))
