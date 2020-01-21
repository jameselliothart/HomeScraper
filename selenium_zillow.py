from datetime import datetime
from urllib3.exceptions import ProtocolError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from contextlib import contextmanager
from bs4 import BeautifulSoup
from collections import namedtuple
import pandas as pd
import json
import unicodedata
import time
import os


# url = 'https://www.zillow.com/homes/for_sale/house_type/3-_beds/2.0-_baths/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-95.76427426757812,%22east%22:-95.3625866455078,%22south%22:29.66314808323101,%22north%22:29.90569536762166},%22isMapVisible%22:true,%22mapZoom%22:12,%22filterState%22:{%22price%22:{%22min%22:300000,%22max%22:500000},%22monthlyPayment%22:{%22min%22:1097,%22max%22:1829},%22beds%22:{%22min%22:3},%22isManufactured%22:{%22value%22:false},%22isCondo%22:{%22value%22:false},%22isMultiFamily%22:{%22value%22:false},%22isApartment%22:{%22value%22:false},%22isLotLand%22:{%22value%22:false},%22isTownhouse%22:{%22value%22:false},%22baths%22:{%22min%22:2},%22hoa%22:{%22max%22:200},%22hasAirConditioning%22:{%22value%22:true},%22hasGarage%22:{%22value%22:true},%22built%22:{%22min%22:2015}},%22isListVisible%22:true}'
# url = 'https://www.zillow.com/homes/for_sale/house_type/3-_beds/2.0-_baths/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-95.77269044767343,%22east%22:-95.57184663663827,%22south%22:29.72443627345869,%22north%22:29.845709239371146},%22mapZoom%22:13,%22isMapVisible%22:true,%22filterState%22:{%22price%22:{%22min%22:200000,%22max%22:500000},%22monthlyPayment%22:{%22min%22:740,%22max%22:1829},%22beds%22:{%22min%22:3},%22isManufactured%22:{%22value%22:false},%22isCondo%22:{%22value%22:false},%22isMultiFamily%22:{%22value%22:false},%22isApartment%22:{%22value%22:false},%22isLotLand%22:{%22value%22:false},%22isTownhouse%22:{%22value%22:false},%22baths%22:{%22min%22:2},%22hasAirConditioning%22:{%22value%22:true},%22hasGarage%22:{%22value%22:true},%22built%22:{%22min%22:2010}},%22isListVisible%22:true}'

@contextmanager
def open_driver(web_driver='chromedriver_linux64/chromedriver', options=Options()):
    driver = webdriver.Chrome(web_driver, options=options)
    yield driver
    driver.quit()


def check_captcha_challenge(driver, xpath="//iframe[@title='recaptcha challenge']"):
    captcha = driver.find_elements_by_xpath(xpath)
    if captcha:
        _ = input("Please solve captcha...")
    return driver


def get_url(driver, url):
    driver.get(url)
    driver = check_captcha_challenge(driver)
    return driver


def get_detail_links(page_source, class_identifier='list-card-link'):
    soup = BeautifulSoup(page_source, 'lxml')
    link_finder = soup.find_all('a', class_=class_identifier)
    detail_links = [link['href'] for link in link_finder]  # https://www.zillow.com/homedetails/1213-Elberta-St-Houston-TX-77051/27864812_zpid/
    return detail_links


def accumulate_detail_links(driver, url):
    detail_links = set()
    driver = get_url(driver, url)
    while True:
        try:
            time.sleep(1)
            page_links = get_detail_links(driver.page_source)
            detail_links.update(page_links)
            driver.find_element_by_xpath("//a[@aria-label='NEXT Page']").click()
        except NoSuchElementException:
            print('No more NEXT')
            break
    return list(detail_links)


def empty_home_info(url=None):
    attributes = ['Price','Address','Bed','Bath','Sqft','Type','Yearbuilt','Heating','Cooling','Parking','Lot','Pricesqft','Schools','Link']
    home_info = {k:None for k in attributes}
    home_info['Link'] = url
    return home_info


def get_home_info(page_source, url=None):
    # home = namedtuple('house', ['Price', 'Address', 'Bed', 'Bath', 'Sqft', 'Type', 'Yearbuilt', 'Heating', 'Cooling', 'Parking', 'Lot', 'Pricesqft', 'Schools'])
    soup_home = BeautifulSoup(page_source, 'lxml')
    try:
        # basic info: value, address, size
        home_info = empty_home_info(url)
        price_raw = soup_home.find('span', class_='ds-value').text
        address_raw = soup_home.find('h1', class_='ds-address-container').text
        bed_bath = soup_home.find('h3', class_='ds-bed-bath-living-area-container').contents
        home_info['Price'] = int(price_raw.replace('$','').replace(',',''))
        home_info['Address'] = unicodedata.normalize("NFKD", address_raw)
        home_info['Bed'], home_info['Bath'], home_info['Sqft'] = [x.text for x in bed_bath if x.text]

        # home facts (year built, parking, lot size, etc)
        fact_list = soup_home.find('ul', class_='ds-home-fact-list').contents
        home_facts = {fact_tuple[0].replace(' ','').replace('/',''): fact_tuple[1] for fact_tuple in [fact.text.split(':') for fact in fact_list]}
        home_info.update(home_facts)

        # school info
        schools = soup_home.find('div', class_='ds-nearby-schools-list').contents
        school_ratings = [school.find('span', class_='ds-schools-display-rating').text for school in schools]
        home_info['Schools'] = '|'.join(school_ratings)
        # home_info['Schools'] = [
        #     (
        #         int(school.find('span', class_='ds-schools-display-rating').text),
        #         school.find('a', class_='ds-school-name').text,
        #         school.find('a', class_='ds-school-name')['href']
        #     )
        #     for school in schools
        # ]
    except AttributeError:
        print(f'Could not get some attributes for {url}')

    return home_info


def scrape_home_info(driver, url):
    driver = get_url(driver, url)
    home_info = get_home_info(driver.page_source, url)
    return home_info


def accumulate_home_info(driver, detail_links):
    all_home_info = []
    for link in detail_links:
        time.sleep(1)
        home_info = scrape_home_info(driver, link)
        all_home_info.append(home_info)
    return all_home_info


def persist_links(links, filename=None):
    file_name = filename or f'home_detail_links_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
    with open(file_name, 'w') as f:
        for link in links:
            print(link, file=f)


def write_to_csv(home_info, filename='home_info.csv', sep=","):
    df = pd.DataFrame(home_info)

    if not os.path.isfile(filename):
        df.to_csv(filename, mode='a', index=False, sep=sep)
    elif len(df.columns) != len(pd.read_csv(filename, nrows=1, sep=sep).columns):
        raise Exception("Columns do not match!! Dataframe has " + str(len(df.columns)) + " columns. CSV file has " + str(len(pd.read_csv(filename, nrows=1, sep=sep).columns)) + " columns.")
    elif not (df.columns == pd.read_csv(filename, nrows=1, sep=sep).columns).all():
        raise Exception("Columns and column order of dataframe and csv file do not match!!")
    else:
        df.to_csv(filename, mode='a', index=False, sep=sep, header=False)


def read_file_content(filename):
    with open(filename, 'r') as file:
        content = [line.rstrip() for line in file]
    return content


def get_last_processed_link(filename):
    try:
        content = pd.read_csv(filename)
        return content.Link.iat[-1]
    except Exception:
        return None


if __name__ == "__main__":
    CHROME_DRIVER = "/home/james/source/repos/zillow/chromedriver_linux64/chromedriver"
    url = 'https://www.zillow.com/homes/for_sale/house_type/3-_beds/2.0-_baths/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-96.14231603525764,%22east%22:-95.33894079111701,%22south%22:29.50655564051075,%22north%22:29.991819056460194},%22mapZoom%22:11,%22isMapVisible%22:true,%22filterState%22:{%22price%22:{%22min%22:200000,%22max%22:500000},%22monthlyPayment%22:{%22min%22:740,%22max%22:1829},%22beds%22:{%22min%22:3},%22isManufactured%22:{%22value%22:false},%22isCondo%22:{%22value%22:false},%22isMultiFamily%22:{%22value%22:false},%22isApartment%22:{%22value%22:false},%22isLotLand%22:{%22value%22:false},%22isTownhouse%22:{%22value%22:false},%22baths%22:{%22min%22:2},%22hasAirConditioning%22:{%22value%22:true},%22hasGarage%22:{%22value%22:true},%22built%22:{%22min%22:2010}},%22isListVisible%22:true,%22customRegionId%22:%22305935e1e6X1-CR1mc5ok4wc7eda_zb89y%22}'
    home_info_csv = 'home_info.csv'
    home_links = read_file_content('home_detail_links.txt')
    while get_last_processed_link(home_info_csv) != home_links[-1]:
        start = home_links.index(get_last_processed_link(home_info_csv)) + 1 if get_last_processed_link(home_info_csv) else 0
        try:
            with open_driver(CHROME_DRIVER) as driver:
                for link in home_links[start:]:
                    try:
                        time.sleep(1)
                        home_info = scrape_home_info(driver, link)
                    except AttributeError:
                        print(f'Failure on {link}')
                        continue
                    else:
                        write_to_csv([home_info], home_info_csv)
        except ProtocolError:
            print('Continuing after ProtocolError...')
            continue
