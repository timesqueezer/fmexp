import time
import random

import pyautogui

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from faker import Faker

from fmbot.bot import Bot


class MouseBot(Bot):
    def __init__(self, target_host, random_delays=False, advanced=False):
        super().__init__(target_host, 'mouse', random_delays=random_delays, advanced=advanced)

        self.fake = Faker()

        # self.driver.execute_script('const borderWidth = (window.outerWidth - window.innerWidth) / 2')
        # self.window_x = self.driver.execute_script('return window.screenLeft + window.pageXOffset')
        self.window_x = self.driver.execute_script('return window.screenX')
        self.window_y = self.driver.execute_script('return (window.outerHeight - window.innerHeight) + window.screenY')

        print('window_x', self.window_x)
        print('window_y', self.window_y)

    def move_click(self, el):
        self.scroll_wait(el)

        if not self.advanced:
            self.get_ac().move_to_element(el).perform()
            self.get_ac().click().perform()

        else:
            self.random_wait()

            rd = 500
            if self.random_delays:
                rd = random.randint(0, 2000)

            # click_offset = 10
            # wat
            click_offset_x = 25
            click_offset_y = 50

            x = el.location['x'] + self.window_x + click_offset_x
            y = el.location['y'] + self.window_y + click_offset_y

            """print('hmmm', x, y)
            print(
                self.driver.execute_script('return document.getElementById("consentButton").getBoundingClientRect().y')
            )
            print(el.location)"""

            pyautogui.moveTo(x, y, duration=(rd / 1000), tween=pyautogui.easeInOutCubic)

            self.random_wait()

            pyautogui.mouseDown()
            self.random_wait(upper_limit=200)
            pyautogui.mouseUp()
            # pyautogui.click()

    def check_go_button(self):
        try:
            go_button = self.find_element_by_xpath('//button[text() = "Let\'s go"]')

        except NoSuchElementException:
            return

        self.move_click(go_button)

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

            self.move_click(link_el)

    def visit_blog_pages(self, num_pages=10):
        self.check_go_button()

        link_el = self.find_element_by_xpath('//a[@href="/blog"]')
        self.move_click(link_el)

        for i in range(num_pages):
            all_link_els = self.find_elements_by_xpath('//main//a')
            selected_link = random.choice(all_link_els)

            self.move_click(selected_link)

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

            self.move_click(el)

    def register(self):
        self.check_go_button()

        link_el = self.find_element_by_xpath('//a[@href="/register"]')
        self.move_click(link_el)

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
        self.move_click(not_robot_el)

        submit_el = self.find_element_by_xpath('//button[@type="submit"]')
        self.move_click(submit_el)

    def register_and_fill_in_profile(self):
        self.check_go_button()

        link_el = self.find_element_by_xpath('//a[@href="/register"]')
        self.move_click(link_el)

        email_input_el = self.find_element_by_id('email')
        email_input_el.send_keys(self.fake.email())

        password = self.fake.word()

        password1_input_el = self.find_element_by_id('password')
        password1_input_el.send_keys(password)

        password2_input_el = self.find_element_by_id('password2')
        password2_input_el.send_keys(password)

        not_robot_el = self.find_element_by_id('not_robot')
        self.move_click(not_robot_el)

        submit_el = self.find_element_by_xpath('//button[@type="submit"]')
        self.move_click(submit_el)
