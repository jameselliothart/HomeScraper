import unicodedata
from collections import OrderedDict
from bs4 import BeautifulSoup


class Home():
    ATTRIBUTES = ['Price','Address','Bed','Bath','Sqft','Type','Yearbuilt','Heating','Cooling','Parking','Lot','Pricesqft','Schools','Link']

    def __init__(self, page_source=None, url=None):
        self.soup = BeautifulSoup(page_source, 'lxml') if page_source else None
        self.info = OrderedDict([(attribute, None) for attribute in Home.ATTRIBUTES])
        self.info['Link'] = url

    @staticmethod
    def create_from_keywords(**kwargs):
        home = Home()
        home.info.update({k: v for k, v in kwargs.items() if k in Home.ATTRIBUTES})
        return home

    @staticmethod
    def _sanitize_home_fact(fact):
        return fact.replace(' ','').replace('/','')

    def _update_price(self, soup):
        price_raw = soup.find('span', class_='ds-value').text
        self.info['Price'] = int(price_raw.replace('$','').replace(',',''))

    def _update_address(self, soup):
        address_raw = soup.find('h1', class_='ds-address-container').text
        self.info['Address'] = unicodedata.normalize("NFKD", address_raw)

    def _update_bed_bath(self, soup):
        bed_bath = soup.find('h3', class_='ds-bed-bath-living-area-container').contents
        self.info['Bed'], self.info['Bath'], self.info['Sqft'] = [x.text for x in bed_bath if x.text]

    def update_basic_home_info(self, soup):
        self._update_price(soup)
        self._update_address(soup)
        self._update_bed_bath(soup)

    def update_home_facts(self, soup):
        fact_list = soup.find('ul', class_='ds-home-fact-list').contents
        fact_tuples = [fact.text.split(':') for fact in fact_list]
        home_facts = {self._sanitize_home_fact(fact_tuple[0]): fact_tuple[1] for fact_tuple in fact_tuples if fact_tuple[0] in Home.ATTRIBUTES}
        self.info.update(home_facts)

    def update_school_info(self, soup):
        schools = soup.find('div', class_='ds-nearby-schools-list').contents
        school_ratings = [school.find('span', class_='ds-schools-display-rating').text for school in schools]
        self.info['Schools'] = '|'.join(school_ratings)

    def __repr__(self):
        return repr(self.info)
