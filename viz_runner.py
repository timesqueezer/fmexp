import argparse

from fmexp import create_app
from fmexp.fmviz.user_hist import user_hist
from fmexp.fmviz.roc_curves import roc_curves
from fmexp.fmviz.mouse_heatmap import mouse_heatmap


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Visualization Runner')
    parser.add_argument('-m', default='roc_curves', required=False, dest='mode')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.mode == 'user_hist':
            user_hist()

        elif args.mode == 'roc_curves':
            roc_curves()

        elif args.mode == 'mouse_heatmap':
            mouse_heatmap()
