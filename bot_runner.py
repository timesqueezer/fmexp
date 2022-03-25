from fmbot.request_bot import RequestBot
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FMEXP Bot Runner')
    parser.add_argument('-m', default='request', required=False, dest='mode')
    parser.add_argument('-t', default='http://10.1.1.111:5002', required=False, dest='target')
    args = parser.parse_args()

    if args.mode == 'request':
        request_bot = RequestBot(args.target)
        print('visit_pages')
        request_bot.visit_pages()
        print('visit_blog_pages')
        request_bot.visit_blog_pages()
        print('visit_random_pages')
        request_bot.visit_random_pages()
        print('register')
        request_bot.register()
