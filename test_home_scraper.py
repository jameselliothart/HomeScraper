import pytest
from collections import OrderedDict
from selenium.webdriver.chrome.options import Options
from home import Home
from scraper import WebScraper, open_driver


class TestHome():
    @pytest.fixture(scope='session')
    def home_detail_source(self):
        with open('resources/home_detail.html', 'r') as f:
            yield f.read()

    def test_home_gets_basic_info(self, home_detail_source):
        sut_home = Home(home_detail_source)

        sut_home.update_basic_home_info()

        expected = {'Price':209000, 'Address':'6015 Crakston St, Houston, TX 77084', 'Bed':'3 bd', 'Bath':'2 ba', 'Sqft':'1,906 sqft'}
        assert sut_home.info == Home.create_info_from_keywords(**expected).info

    def test_home_gets_facts(self, home_detail_source):
        sut_home = Home(home_detail_source)

        sut_home.update_home_facts()

        expected = {'Cooling': 'Central', 'Lot': '5,501 sqft', 'Type': 'Single Family', 'Yearbuilt':'2012', 'Pricesqft':'$110', 'Heating': 'Other', 'Parking': '2 spaces'}
        assert sut_home.info == Home.create_info_from_keywords(**expected).info

    def test_home_gets_school_info(self, home_detail_source):
        sut_home = Home(home_detail_source)

        sut_home.update_school_info()

        expected = {'Schools': '4|5|7'}
        assert sut_home.info == Home.create_info_from_keywords(**expected).info

    def test_sanitize_home_fact_removes_space(self):
        assert Home._sanitize_home_fact('Year built') == 'Yearbuilt'

    def test_sanitize_home_fact_removes_slash(self):
        assert Home._sanitize_home_fact('Price/sqft') == 'Pricesqft'


class TestScraper():
    @pytest.fixture(scope='session')
    def driver(self):
        options = Options()
        options.add_argument("--headless")
        with open_driver(options=options) as driver:
            yield driver

    def test_driver_initializes(self, driver):
        assert True

    def test_identifies_captcha_when_exists(self, driver):
        driver.get('https://www.tutdepot.com/demos/custom-captcha-image-script/')
        actual = driver.check_captcha_challenge(handle_captcha=(lambda : 'identified captcha'))
        assert actual == 'identified captcha'

    def test_no_callback_when_no_captcha(self, driver):
        driver.get('https://www.google.com/')
        actual = driver.check_captcha_challenge()
        assert actual is None

    def test_get_detail_links(self):
        with open('resources/expected_links.txt', 'r') as f:
            expected = [line.rstrip() for line in f]
        with open('resources/search_results.html', 'r') as f:
            page_source = f.read()
        actual = WebScraper.get_detail_links(page_source)
        assert actual == expected
