import argparse

from fmexp import create_app
from fmexp.fmviz.user_hist import user_hist
from fmexp.fmviz.roc_curves import roc_curves
from fmexp.fmviz.mouse_heatmap import mouse_heatmap
from fmexp.fmviz.mouse_hist import mouse_hist
from fmexp.fmviz.mouse_debug import mouse_debug
from fmexp.fmviz.speed_per_dp_count import speed_per_dp_count
from fmexp.fmviz.model_parameters import model_parameters


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Visualization Runner')
    parser.add_argument('-v', default='roc_curves', required=False, dest='viz_mode')
    parser.add_argument('-m', default='request', required=False, dest='mode', choices=['request', 'request_advanced', 'mouse', 'mouse_advanced', 'mouse_dataset'])
    parser.add_argument('-i', default='fmexp', required=False, dest='instance', choices=['fmexp', 'fmexp2'])
    args = parser.parse_args()
    mode = args.mode
    instance = args.instance


    if args.viz_mode == 'user_hist':
        app = create_app()
        with app.app_context():
            user_hist()

    elif args.viz_mode == 'bot_hist':
        app = create_app()
        with app.app_context():
            user_hist(bot=True)

    elif args.viz_mode == 'roc_curves':
        roc_curves(
            modes=[
                # 'fmexp_cache_mouse_dataset21_users.json',
                # 'fmexp_cache_mouse_dataset_user1.json',
                'mouse_advanced',
            ],
            instances=['fmexp1', 'fmexp2'],
        )

    elif args.viz_mode == 'mouse_heatmap':
        mouse_heatmap()

    elif args.viz_mode == 'mouse_hist':
        mouse_hist()

    elif args.viz_mode == 'mouse_debug':
        mouse_debug()

    elif args.viz_mode == 'speed_per_dp_count':
        speed_per_dp_count()

    elif args.viz_mode == 'model_parameters':
        model_parameters()
