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


CHROME_DRIVER = "/home/james/source/repos/zillow/chromedriver_linux64/chromedriver"
url = 'https://www.zillow.com/homes/for_sale/house_type/3-_beds/2.0-_baths/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-96.14231603525764,%22east%22:-95.33894079111701,%22south%22:29.50655564051075,%22north%22:29.991819056460194},%22mapZoom%22:11,%22isMapVisible%22:true,%22filterState%22:{%22price%22:{%22min%22:200000,%22max%22:500000},%22monthlyPayment%22:{%22min%22:740,%22max%22:1829},%22beds%22:{%22min%22:3},%22isManufactured%22:{%22value%22:false},%22isCondo%22:{%22value%22:false},%22isMultiFamily%22:{%22value%22:false},%22isApartment%22:{%22value%22:false},%22isLotLand%22:{%22value%22:false},%22isTownhouse%22:{%22value%22:false},%22baths%22:{%22min%22:2},%22hasAirConditioning%22:{%22value%22:true},%22hasGarage%22:{%22value%22:true},%22built%22:{%22min%22:2010}},%22isListVisible%22:true,%22customRegionId%22:%22305935e1e6X1-CR1mc5ok4wc7eda_zb89y%22}'
# url = 'https://www.zillow.com/homes/for_sale/house_type/3-_beds/2.0-_baths/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-95.76427426757812,%22east%22:-95.3625866455078,%22south%22:29.66314808323101,%22north%22:29.90569536762166},%22isMapVisible%22:true,%22mapZoom%22:12,%22filterState%22:{%22price%22:{%22min%22:300000,%22max%22:500000},%22monthlyPayment%22:{%22min%22:1097,%22max%22:1829},%22beds%22:{%22min%22:3},%22isManufactured%22:{%22value%22:false},%22isCondo%22:{%22value%22:false},%22isMultiFamily%22:{%22value%22:false},%22isApartment%22:{%22value%22:false},%22isLotLand%22:{%22value%22:false},%22isTownhouse%22:{%22value%22:false},%22baths%22:{%22min%22:2},%22hoa%22:{%22max%22:200},%22hasAirConditioning%22:{%22value%22:true},%22hasGarage%22:{%22value%22:true},%22built%22:{%22min%22:2015}},%22isListVisible%22:true}'
# url = 'https://www.zillow.com/homes/for_sale/house_type/3-_beds/2.0-_baths/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-95.77269044767343,%22east%22:-95.57184663663827,%22south%22:29.72443627345869,%22north%22:29.845709239371146},%22mapZoom%22:13,%22isMapVisible%22:true,%22filterState%22:{%22price%22:{%22min%22:200000,%22max%22:500000},%22monthlyPayment%22:{%22min%22:740,%22max%22:1829},%22beds%22:{%22min%22:3},%22isManufactured%22:{%22value%22:false},%22isCondo%22:{%22value%22:false},%22isMultiFamily%22:{%22value%22:false},%22isApartment%22:{%22value%22:false},%22isLotLand%22:{%22value%22:false},%22isTownhouse%22:{%22value%22:false},%22baths%22:{%22min%22:2},%22hasAirConditioning%22:{%22value%22:true},%22hasGarage%22:{%22value%22:true},%22built%22:{%22min%22:2010}},%22isListVisible%22:true}'


@contextmanager
def open_driver(options=Options()):
    driver = webdriver.Chrome(CHROME_DRIVER, options=options)
    yield driver
    driver.quit()


def get_page_source(driver, url):
    print(f'Getting {url}')
    driver.get(url)
    page_source = driver.page_source
    return page_source


def get_detail_links(page_source, class_identifier='list-card-link'):
    soup = BeautifulSoup(page_source, 'lxml')
    link_finder = soup.find_all('a', class_=class_identifier)
    detail_links = [link['href'] for link in link_finder]  # https://www.zillow.com/homedetails/1213-Elberta-St-Houston-TX-77051/27864812_zpid/
    return detail_links


def get_home_info(soup_home):
    # home = namedtuple('house', ['Price', 'Address', 'Bed', 'Bath', 'Sqft', 'Type', 'Yearbuilt', 'Heating', 'Cooling', 'Parking', 'Lot', 'Pricesqft', 'Schools'])
    home_info = {}

    # basic info: value, address, size
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
    return home_info


# can use options to avoid loading images, use disk cache, headless browser
chrome_options = Options()
# chrome_options.add_argument("start-maximized")

# need to loop here to get all paginated results
all_home_info = []
with open_driver(chrome_options) as driver:
    detail_links = set()
    driver.get(url)
    while True:
        try:
            time.sleep(1)
            page_source = driver.page_source
            page_links = get_detail_links(page_source)
            detail_links.update(page_links)
            driver.find_element_by_xpath("//a[@aria-label='NEXT Page']").click()
        except Exception as e:
            print(f'{e}')
            break
    for link in list(detail_links)[0:3]:
        time.sleep(1)
        detail_source = get_page_source(driver, link)
        detail_soup = BeautifulSoup(detail_source, 'lxml')
        home_info = get_home_info(detail_soup)
        all_home_info.append(home_info)

output_file = 'home_info.csv'
if os.path.exists(output_file):
    os.remove(output_file)
pd.DataFrame(all_home_info).to_csv(output_file, index=False)
