import random

from selenium.common.exceptions import NoSuchElementException

from fmbot.bot import Bot


class RequestBot(Bot):
    def __init__(self, target_host):
        super().__init__(target_host)

    def check_go_button(self):
        try:
            go_button = self.driver.find_element_by_xpath('//button[text() = "Let\'s go"]')

        except NoSuchElementException:
            return

        go_button.click()

    def visit_pages(self):
        self.check_go_button()

        top_level_pages = [
            '/blog',
            '/contact',
            '/login',
            '/register',
        ]

        for tlp in top_level_pages:
            link_el = self.driver.find_element_by_xpath('//a[@href="{}"]'.format(tlp))
            link_el.click()

    def visit_blog_pages(self, num_pages=10):
        self.check_go_button()

        link_el = self.driver.find_element_by_xpath('//a[@href="/blog"]')
        link_el.click()

        for i in range(num_pages):
            all_link_els = self.driver.find_elements_by_xpath('//main//a')
            selected_link = random.choice(all_link_els)
            selected_link.click()
            self.driver.back()

        bot_el = self.driver.find_element_by_id('is-bot')
        print('IS BOT:', bot_el.text)
