from urllib3.exceptions import ProtocolError
from home import Home
from scraper import open_driver, WebScraper
from utility import persist_links, read_file_content, get_last_processed_link, write_to_csv


def get_home_detail_links(url, filename):
    with open_driver() as driver:
        detail_links = driver.get_all_detail_links(url)

    persist_links(detail_links, filename)


def record_home_info(detail_links, filename):
    with open_driver() as driver:
        for link in detail_links:
            home_info = driver.get_url_home_info(link, Home, sleep=1)
            write_to_csv([home_info], filename)


def scrape_home_urls(detail_links_file, output_csv):
    home_links = read_file_content(detail_links_file)
    while get_last_processed_link(output_csv) != home_links[-1]:
        start = home_links.index(get_last_processed_link(output_csv)) + 1 if get_last_processed_link(output_csv) else 0
        try:
            record_home_info(home_links[start:], output_csv)
        except ProtocolError:
            print('Continuing after ProtocolError...')
            continue


output_csv = 'output/home_info_20200127.csv'
detail_links_file = 'output/home_detail_links_20200127.txt'
url = 'https://www.zillow.com/homes/for_sale/house_type/3-_beds/2.0-_baths/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-95.74911361776299,%22east%22:-95.54826980672783,%22south%22:29.69765283547883,%22north%22:29.818958215684205},%22mapZoom%22:13,%22customRegionId%22:%22551dd5e2ddX1-CR1s17jaao006f2_13dbf2%22,%22isMapVisible%22:true,%22filterState%22:{%22price%22:{%22min%22:0,%22max%22:500000},%22monthlyPayment%22:{%22min%22:0,%22max%22:1843},%22beds%22:{%22min%22:3},%22baths%22:{%22min%22:2},%22sortSelection%22:{%22value%22:%22globalrelevanceex%22},%22hasGarage%22:{%22value%22:true},%22hasAirConditioning%22:{%22value%22:true},%22isCondo%22:{%22value%22:false},%22isMultiFamily%22:{%22value%22:false},%22isManufactured%22:{%22value%22:false},%22isLotLand%22:{%22value%22:false},%22isTownhouse%22:{%22value%22:false},%22isApartment%22:{%22value%22:false}},%22isListVisible%22:true}'


if __name__ == "__main__":
    # get_home_detail_links(url, detail_links_file)
    scrape_home_urls(detail_links_file, output_csv)
