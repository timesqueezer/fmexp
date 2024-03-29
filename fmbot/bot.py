import time
import random

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options


RESOLUTIONS = [
    (1920, 1080),
    (1366, 768),
    (2560, 1440),
]


class Bot:
    def __init__(self, target_host, mode, random_delays=False, advanced=False, instance='fmexp'):
        self.width = RESOLUTIONS[0][0]
        self.height = RESOLUTIONS[0][1]

        self.advanced_mouse = mode == 'mouse' and advanced is True

        self.target_host = target_host
        self.random_delays = random_delays
        self.advanced = advanced

        self.instance = instance

        if not self.advanced_mouse:
            options = Options()
            # options.headless = True
            self.driver = webdriver.Firefox(options=options)
            self.driver.set_window_size(self.width, self.height)
            self.driver.implicitly_wait(2)

            # need first request to be able to set cookie
            self.get('/?fmexp_bot=true&bot_mode={}&random_delays={}&advanced={}'.format(
                mode,
                str(random_delays).lower(),
                str(advanced).lower(),
            ))

            self.driver.add_cookie({
                'name': 'fmexp_bot',
                'value': '1',
            })

    def __del__(self):
        if not self.advanced_mouse:
            self.driver.close()

    def get(self, url):
        full_url = self.target_host + url
        return self.driver.get(full_url)

    def random_wait(self, upper_limit=2000):
        if self.random_delays:
            ri = random.randint(0, upper_limit)

            time.sleep(ri / 1000)

    def get_scroll_y(self):
        return self.driver.execute_script('return window.scrollY')

    def scroll_to(self, y):
        self.driver.execute_script('window.scrollTo(0, {});'.format(y))

    def scroll_wait(self, el):
        self.random_wait()

        scroll_y = self.get_scroll_y()
        # print(el.location['y'], scroll_y, self.height + scroll_y)
        # time.sleep(3)

        if el.location['y'] > (self.height + scroll_y):
            self.scroll_to(el.location['y'] - self.height + scroll_y - 100)

        elif el.location['y'] <= (scroll_y):
            self.scroll_to(el.location['y'] - 100)

        WebDriverWait(self.driver, 5) \
            .until(EC.element_to_be_clickable(el))

    def find_element_by_xpath(self, *args, **kwargs):
        self.random_wait()

        return self.driver.find_element_by_xpath(*args, **kwargs)

    def find_elements_by_xpath(self, *args, **kwargs):
        self.random_wait()

        return self.driver.find_elements_by_xpath(*args, **kwargs)

    def find_element_by_id(self, *args, **kwargs):
        self.random_wait()

        return self.driver.find_element_by_id(*args, **kwargs)

    def send_keys(self, target, *args, **kwargs):
        self.random_wait()

        return target.send_keys(*args, **kwargs)

    def click(self, target, *args, **kwargs):
        self.random_wait()

        return target.click(*args, **kwargs)

    def back(self):
        self.random_wait()

        return self.driver.back()

    def get_ac(self):
        self.random_wait()

        if self.random_delays:
            return ActionChains(self.driver, duration=random.randint(100, 2000))
