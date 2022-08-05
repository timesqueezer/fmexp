import argparse
import random

import subprocess

from multiprocessing import Process, cpu_count

from fmbot.request_bot import RequestBot
from fmbot.mouse_bot import MouseBot


def run_request_bot(i, n, runs_per_proc, random_delays, advanced, instance):
    methods = [
        'visit_pages',
        'visit_blog_pages',
        'visit_random_pages',
        'register',
        'register_and_fill_in_profile',
    ]

    for run_counter in range(runs_per_proc):
        try:
            request_bot = RequestBot(
                args.target,
                random_delays=random_delays,
                advanced=advanced,
                instance=instance,
            )

            shuffled_methods = random.sample(methods, len(methods))
            for method in shuffled_methods:
                getattr(request_bot, method)()

        except Exception as e:
            print(f'[{i}] Run: {run_counter}. HERP DERP:', e)


def run_mouse_bot(i, n, runs_per_proc, random_delays, advanced, instance):
    methods = [
        'visit_pages',
        'visit_blog_pages',
        'visit_random_pages',
        'register',
        # 'register_and_fill_in_profile',
    ]

    for run_counter in range(runs_per_proc):
        try:
            mouse_bot = MouseBot(
                args.target,
                random_delays=random_delays,
                advanced=advanced,
                instance=instance,
            )

            shuffled_methods = random.sample(methods, len(methods))
            if not mouse_bot.advanced_mouse:
                for method in shuffled_methods:
                    getattr(mouse_bot, method)()

            else:
                subprocess.run([
                    'node',
                    'fmexp/templates/frontend/src/advanced-mouse-bot.js',
                    mouse_bot.target_host,
                    str(mouse_bot.width),
                    str(mouse_bot.height),
                    *shuffled_methods,
                ])

        except Exception as e:
            print(f'[{i}] Run: {run_counter}. HERP DERP:', e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Bot Runner')
    parser.add_argument('-m', default='request', required=False, dest='mode', choices=['request', 'request_advanced', 'mouse', 'mouse_advanced'])
    parser.add_argument('-t', default='http://localhost:5002', required=False, dest='target')
    parser.add_argument('-n', default=1, required=False, dest='num_runs', type=int)
    parser.add_argument('-r', default=True, required=False, dest='random_delays')
    parser.add_argument('-i', default='fmexp', required=False, dest='instance', choices=['fmexp', 'fmexp2'])

    args = parser.parse_args()
    num_runs = args.num_runs
    random_delays = args.random_delays

    instance = args.instance

    cpu_count = cpu_count() * 2
    PROCESSES = cpu_count if num_runs >= cpu_count else num_runs
    runs_per_proc = num_runs // PROCESSES

    print('Mode:', args.mode)
    print(num_runs, 'run on', PROCESSES, 'Processes')
    print('Runs per Process:', runs_per_proc)
    print('Random Delays:', random_delays)

    p_list = []

    advanced = False
    target = None
    if args.mode == 'request':
        target = run_request_bot

    if args.mode == 'mouse':
        target = run_mouse_bot

    if args.mode == 'request_advanced':
        target = run_request_bot
        advanced = True

    if args.mode == 'mouse_advanced':
        target = run_mouse_bot
        advanced = True

    else:
        pass


    print('Starting {} processes'.format(PROCESSES))
    for i in range(PROCESSES):
        p = Process(target=target, args=(i, PROCESSES, runs_per_proc, random_delays, advanced, instance, ))
        p_list.append(p)
        p.start()

    for p in p_list:
        p.join()

    print('Done')
