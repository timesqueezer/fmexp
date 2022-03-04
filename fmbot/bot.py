from selenium import webdriver


class Bot:
    def __init__(self, target_host):
        self.driver = webdriver.Firefox()
        self.driver.set_window_size(1200, 800)
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
