import argparse

from fmexp import create_app
from fmexp.fmviz.user_hist import user_hist


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Visualization Runner')
    parser.add_argument('-m', default='user_hist', required=False, dest='mode')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.mode == 'user_hist':
            user_hist()
