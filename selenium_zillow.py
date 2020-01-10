from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from collections import namedtuple
import unicodedata


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
    home_info['Schools'] = [
        (
            int(school.find('span', class_='ds-schools-display-rating').text),
            school.find('a', class_='ds-school-name').text,
            school.find('a', class_='ds-school-name')['href']
        )
        for school in schools
    ]
    return home_info


CHROME_DRIVER = "/home/james/source/repos/zillow/chromedriver_linux64/chromedriver"
url = 'https://www.zillow.com/homes/for_sale/house_type/3-_beds/2.0-_baths/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-95.76427426757812,%22east%22:-95.3625866455078,%22south%22:29.66314808323101,%22north%22:29.90569536762166},%22isMapVisible%22:true,%22mapZoom%22:12,%22filterState%22:{%22price%22:{%22min%22:300000,%22max%22:500000},%22monthlyPayment%22:{%22min%22:1097,%22max%22:1829},%22beds%22:{%22min%22:3},%22isManufactured%22:{%22value%22:false},%22isCondo%22:{%22value%22:false},%22isMultiFamily%22:{%22value%22:false},%22isApartment%22:{%22value%22:false},%22isLotLand%22:{%22value%22:false},%22isTownhouse%22:{%22value%22:false},%22baths%22:{%22min%22:2},%22hoa%22:{%22max%22:200},%22hasAirConditioning%22:{%22value%22:true},%22hasGarage%22:{%22value%22:true},%22built%22:{%22min%22:2015}},%22isListVisible%22:true}'

# can use options to avoid loading images, use disk cache, headless browser
chrome_options = Options()
chrome_options.add_argument("start-maximized")
driver = webdriver.Chrome(CHROME_DRIVER, options=chrome_options)

child_chrome_options = Options()
# child_chrome_options.add_argument("--headless")

# need to loop here to get all paginated results
driver.get(url)
page_source_overview = driver.page_source
soup = BeautifulSoup(page_source_overview, 'lxml')
link_finder = soup.find_all('a', class_='list-card-link')

# once we have all the home detail links, get info for all of them
detail_links = [link['href'] for link in link_finder]
link = detail_links[0]  # https://www.zillow.com/homedetails/1213-Elberta-St-Houston-TX-77051/27864812_zpid/

# get page source for a home from url
child_driver = webdriver.Chrome(CHROME_DRIVER, options=child_chrome_options)
child_driver.get(link)
home_source_info = child_driver.page_source
soup_home = BeautifulSoup(home_source_info, 'lxml')

home_info = get_home_info(soup_home)
print(home_info)
