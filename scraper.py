from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from contextlib import contextmanager


@contextmanager
def open_driver(web_driver='./chromedriver', options=Options()):
    driver = WebScraper(web_driver, options=options)
    yield driver
    driver.quit()


class WebScraper(webdriver.Chrome):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _handle_captcha(self):
        return input("Please solve captcha...")

    def check_captcha_challenge(self, handle_captcha=None, xpath="//iframe[@title='recaptcha challenge']"):
        captcha_handler = self._handle_captcha if handle_captcha is None else handle_captcha
        captcha = self.find_elements_by_xpath(xpath)
        if captcha:
            return captcha_handler()
        return None

    def safe_get(self, url):
        self.get(url)
        _ = self.check_captcha_challenge()

