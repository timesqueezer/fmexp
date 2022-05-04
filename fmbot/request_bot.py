import time
import random

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains

from faker import Faker

from fmbot.bot import Bot


class RequestBot(Bot):
    def __init__(self, target_host, random_delays=False, advanced=False):
        super().__init__(target_host, 'request', random_delays=random_delays, advanced=advanced)

        self.fake = Faker()

    def check_go_button(self):
        try:
            go_button = self.find_element_by_xpath('//button[text() = "Let\'s go"]')

        except NoSuchElementException:
            return

        self.click(go_button)

    def visit_pages(self):
        self.check_go_button()

        top_level_pages = [
            '/blog',
            '/contact',
            '/login',
            '/register',
        ]

        for tlp in top_level_pages:
            link_el = self.find_element_by_xpath('//a[@href="{}"]'.format(tlp))
            self.click(link_el)

    def visit_blog_pages(self, num_pages=10):
        self.check_go_button()

        link_el = self.find_element_by_xpath('//a[@href="/blog"]')
        self.click(link_el)

        for i in range(num_pages):
            all_link_els = self.find_elements_by_xpath('//main//a')
            selected_link = random.choice(all_link_els)

            self.scroll_wait(selected_link)

            self.click(selected_link)
            self.back()

    def visit_random_pages(self, num_pages=100):
        self.check_go_button()

        for i in range(num_pages):
            link_els = self.find_elements_by_xpath('//a')
            el = random.choice(link_els)

            # skip external links
            href = el.get_attribute('href')
            if 'matzradloff.info' in href:
                continue

            self.scroll_wait(el)
            self.click(el)

    def register(self):
        self.check_go_button()

        link_el = self.find_element_by_xpath('//a[@href="/register"]')
        self.click(link_el)

        email_input_el = self.find_element_by_id('email')
        fake_email = self.fake.email()

        fake_email_split = fake_email.split('@')
        fake_email = ''.join([
            fake_email_split[0],
            str(random.randint(1, 1000000)),
            '@',
            fake_email_split[1],
        ])

        email_input_el.send_keys(fake_email)

        # make sure its longer than 8 chars
        password = '{}_{}'.format(
            self.fake.word(),
            self.fake.word(),
        )

        password1_input_el = self.find_element_by_id('password')
        password1_input_el.send_keys(password)

        password2_input_el = self.find_element_by_id('password2')
        password2_input_el.send_keys(password)

        not_robot_el = self.find_element_by_id('not_robot')
        self.click(not_robot_el)

        submit_el = self.find_element_by_xpath('//button[@type="submit"]')
        self.click(submit_el)

    def register_and_fill_in_profile(self):
        self.check_go_button()

        link_el = self.find_element_by_xpath('//a[@href="/register"]')
        self.click(link_el)

        email_input_el = self.find_element_by_id('email')
        email_input_el.send_keys(self.fake.email())

        password = self.fake.word()

        password1_input_el = self.find_element_by_id('password')
        password1_input_el.send_keys(password)

        password2_input_el = self.find_element_by_id('password2')
        password2_input_el.send_keys(password)

        not_robot_el = self.find_element_by_id('not_robot')
        self.click(not_robot_el)

        submit_el = self.find_element_by_xpath('//button[@type="submit"]')
        self.click(submit_el)
