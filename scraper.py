import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from contextlib import contextmanager
from bs4 import BeautifulSoup
from home import Home


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
        captcha = self.find_elements_by_xpath(xpath) or 'captchaPerimeter' in self.current_url
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

    def click_by_xpath(self, xpath="//a[@aria-label='NEXT Page']"):
        # expecting to raise NoSuchElementException when button no longer found
        self.find_element_by_xpath(xpath).click()

    def get_all_detail_links(self, search_url):
        detail_links = set()
        self.get(search_url)
        while True:
            try:
                time.sleep(1)  # give time for page to render Next button
                page_links = self.get_current_page_detail_links()
                detail_links.update(page_links)
                self.click_by_xpath()
            except NoSuchElementException:
                print('No more NEXT')
                break
        return list(detail_links)

    def get_url_home_info(self, url, i_home, sleep=0):
        self.get(url)
        time.sleep(sleep)  # give time for page to load
        home = i_home(self.page_source, url)
        home.update_all_info()
        return home.info

    def get_home_info(self, detail_links, i_home=Home, sleep=1):
        return [self.get_url_home_info(link, i_home, sleep) for link in detail_links]
