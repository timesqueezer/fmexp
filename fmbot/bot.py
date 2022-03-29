import time

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Bot:
    def __init__(self, target_host):
        self.width = 1920
        self.height = 1200

        self.driver = webdriver.Firefox()
        self.driver.set_window_size(self.width, self.height)
        self.driver.implicitly_wait(2)

        self.target_host = target_host

        # need first request to be able to set cookie
        self.get('/?fmexp_bot=true')

        self.driver.add_cookie({
            'name': 'fmexp_bot',
            'value': '1',
        })

    def __del__(self):
        self.driver.close()

    def get(self, url):
        full_url = self.target_host + url
        return self.driver.get(full_url)

    def get_scroll_y(self):
        return self.driver.execute_script('return window.scrollY')

    def scroll_to(self, y):
        self.driver.execute_script('window.scrollTo(0, {});'.format(y))

    def scroll_wait(self, el):
        scroll_y = self.get_scroll_y()
        # print(el.location['y'], scroll_y, self.height + scroll_y)
        # time.sleep(3)

        if el.location['y'] > (self.height + scroll_y):
            self.scroll_to(el.location['y'] - self.height + scroll_y - 100)

        elif el.location['y'] <= (scroll_y):
            self.scroll_to(el.location['y'] - 100)

        WebDriverWait(self.driver, 5) \
            .until(EC.element_to_be_clickable(el))
