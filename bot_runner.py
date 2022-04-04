import argparse
import random

from multiprocessing import Process, cpu_count

from fmbot.request_bot import RequestBot


def chunkify(lst, n):
    return [ lst[i::n] for i in range(n) ]


def run_request_bot(i, n, runs_per_proc, random_delays):
    methods = [
        'visit_pages',
        'visit_blog_pages',
        'visit_random_pages',
        'register',
        'register_and_fill_in_profile',
    ]

    for i in range(runs_per_proc):
        request_bot = RequestBot(args.target, random_delays=random_delays)

        shuffled_methods = random.sample(methods, len(methods))
        for method in shuffled_methods:
            try:
                getattr(request_bot, method)()

            except Exception as e:
                print(f'[{i}] HERP DERP:', e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Bot Runner')
    parser.add_argument('-m', default='request', required=False, dest='mode')
    parser.add_argument('-t', default='http://10.1.1.111:5002', required=False, dest='target')
    parser.add_argument('-n', default=12, required=False, dest='num_runs', type=int)
    parser.add_argument('-r', required=False, dest='random_delays', action='store_true')

    args = parser.parse_args()
    num_runs = args.num_runs
    random_delays = args.random_delays

    PROCESSES = cpu_count()
    runs_per_proc = num_runs // PROCESSES
    print(num_runs, 'run on', PROCESSES, 'Processes')
    print('Runs per Process:', runs_per_proc)
    print('Random Delays:', random_delays)

    p_list = []

    print('Starting {} processes'.format(PROCESSES))
    for i in range(PROCESSES):
        target = None
        if args.mode == 'request':
            target = run_request_bot

        else:
            pass

        p = Process(target=target, args=(i, PROCESSES, runs_per_proc, random_delays, ))
        p_list.append(p)
        p.start()

    for p in p_list:
        p.join()

    print('Done')
