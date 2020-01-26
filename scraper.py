from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from contextlib import contextmanager
from bs4 import BeautifulSoup


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

    def check_captcha_challenge(self, handle_captcha, xpath):
        captcha_handler = self._handle_captcha if handle_captcha is None else handle_captcha
        captcha = self.find_elements_by_xpath(xpath)
        if captcha:
            return captcha_handler()
        return None

    def get(self, url, handle_captcha=None, xpath="//iframe[@title='recaptcha challenge']"):
        super().get(url)
        return self.check_captcha_challenge(handle_captcha=handle_captcha, xpath=xpath)

    @staticmethod
    def get_detail_links(page_source, class_identifier='list-card-link'):
        soup = BeautifulSoup(page_source, 'lxml')
        link_finder = soup.find_all('a', class_=class_identifier)
        detail_links = [link['href'] for link in link_finder]  # https://www.zillow.com/homedetails/1213-Elberta-St-Houston-TX-77051/27864812_zpid/
        return detail_links

    def get_current_page_detail_links(self, class_identifier='list-card-link'):
        return self.get_detail_links(self.page_source, class_identifier)
