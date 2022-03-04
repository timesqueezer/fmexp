from fmbot.request_bot import RequestBot
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Bot Runner')
    parser.add_argument('-m', default='request', required=False, dest='mode')
    parser.add_argument('-t', default='http://10.1.1.111:5002', required=False, dest='target')
    args = parser.parse_args()

    if args.mode == 'request':
        request_bot = RequestBot(args.target)
        request_bot.visit_pages()
        request_bot.visit_blog_pages()
