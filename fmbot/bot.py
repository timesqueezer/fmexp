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

    def scroll_wait(self, el):
        print(el.location['y'], self.driver.get_window_position()['y'], self.height - self.driver.get_window_position()['y'])

        if el.location['y'] > (self.height - self.driver.get_window_position()['y']):
            print('scrolling to', el.location['y'] - self.height - self.driver.get_window_position()['y'] - 100)
            self.driver.execute_script('window.scrollTo(0, {});'.format(el.location['y'] - self.height - self.driver.get_window_position()['y'] - 100))

        elif el.location['y'] <= (self.height - self.driver.get_window_position()['y']):
            self.driver.execute_script('window.scrollTo(0, {});'.format(self.height - el.location['y'] + 100))

        WebDriverWait(self.driver, 5) \
            .until(EC.element_to_be_clickable(el))
