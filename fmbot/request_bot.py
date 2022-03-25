import time
import random

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains

from faker import Faker

from fmbot.bot import Bot


class RequestBot(Bot):
    def __init__(self, target_host):
        super().__init__(target_host)

        self.fake = Faker()

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

        print('after blog click')

        for i in range(num_pages):
            all_link_els = self.driver.find_elements_by_xpath('//main//a')
            selected_link = random.choice(all_link_els)

            self.scroll_wait(selected_link)

            selected_link.click()
            self.driver.back()

    def visit_random_pages(self, num_pages=100):
        self.check_go_button()

        for i in range(num_pages):
            link_els = self.driver.find_elements_by_xpath('//a')
            el = random.choice(link_els)
            self.scroll_wait(el)
            el.click()

    def register(self):
        self.check_go_button()

        link_el = self.driver.find_element_by_xpath('//a[@href="/register"]')
        link_el.click()

        email_input_el = self.driver.find_element_by_id('email')
        email_input_el.send_keys(self.fake.email())

        password = self.fake.word()

        password1_input_el = self.driver.find_element_by_id('password')
        password1_input_el.send_keys(password)

        password2_input_el = self.driver.find_element_by_id('password2')
        password2_input_el.send_keys(password)

        not_robot_el = self.driver.find_element_by_id('not_robot')
        not_robot_el.click()

        submit_el = self.driver.find_element_by_xpath('//button[@type="submit"]')
        submit_el.click()
