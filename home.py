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
    def create_info_from_keywords(**kwargs):
        home = Home()
        home.info.update({k: v for k, v in kwargs.items() if k in Home.ATTRIBUTES})
        return home

    @staticmethod
    def _sanitize_home_fact(fact):
        return fact.replace(' ','').replace('/','')

    def _update_price(self):
        price_raw = self.soup.find('span', class_='ds-value').text
        self.info['Price'] = int(price_raw.replace('$','').replace(',',''))

    def _update_address(self):
        address_raw = self.soup.find('h1', class_='ds-address-container').text
        self.info['Address'] = unicodedata.normalize("NFKD", address_raw)

    def _update_bed_bath(self):
        bed_bath = self.soup.find('h3', class_='ds-bed-bath-living-area-container').contents
        self.info['Bed'], self.info['Bath'], self.info['Sqft'] = [x.text for x in bed_bath if x.text]

    def update_basic_home_info(self):
        self._update_price()
        self._update_address()
        self._update_bed_bath()

    def update_home_facts(self):
        # 'Type', 'Yearbuilt', 'Heating', 'Cooling', 'Parking', 'Lot', 'Pricesqft'
        fact_list = self.soup.find('ul', class_='ds-home-fact-list').contents
        fact_tuples = [fact.text.split(':') for fact in fact_list]
        home_facts = {
            self._sanitize_home_fact(fact_tuple[0]): fact_tuple[1] 
            for fact_tuple in fact_tuples
            if self._sanitize_home_fact(fact_tuple[0]) in Home.ATTRIBUTES
        }
        self.info.update(home_facts)

    def update_school_info(self):
        schools = self.soup.find('div', class_='ds-nearby-schools-list').contents
        school_ratings = [school.find('span', class_='ds-schools-display-rating').text for school in schools]
        self.info['Schools'] = '|'.join(school_ratings)

    def update_all_info(self):
        try:
            self.update_basic_home_info()
            self.update_home_facts()
            self.update_school_info()
        except AttributeError:
            print(f'Could not get some attributes for {self.info["Link"]}')

    def __repr__(self):
        return repr(self.info)
