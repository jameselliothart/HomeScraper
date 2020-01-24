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
