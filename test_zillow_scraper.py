from collections import OrderedDict
from bs4 import BeautifulSoup
from home import Home


with open('home_detail.html', 'r') as f:
    home_detail_soup = BeautifulSoup(f.read(), 'lxml')


def test_home_gets_basic_info():
    sut_home = Home()

    sut_home.update_basic_home_info(home_detail_soup)

    expected = {'Price':209000, 'Address':'6015 Crakston St, Houston, TX 77084', 'Bed':'3 bd', 'Bath':'2 ba', 'Sqft':'1,906 sqft'}
    assert sut_home.info == Home.create_from_keywords(**expected).info


def test_home_gets_facts():
    sut_home = Home()

    sut_home.update_home_facts(home_detail_soup)

    expected = {'Cooling': 'Central', 'Lot': '5,501 sqft', 'Type': 'Single Family', 'Heating': 'Other', 'Parking': '2 spaces'}
    assert sut_home.info == Home.create_from_keywords(**expected).info


def test_home_gets_school_info():
    sut_home = Home()

    sut_home.update_school_info(home_detail_soup)

    expected = {'Schools': '4|5|7'}
    assert sut_home.info == Home.create_from_keywords(**expected).info


def test_sanitize_home_fact_removes_space():
    assert Home._sanitize_home_fact('a space') == 'aspace'


def test_sanitize_home_fact_removes_slash():
    assert Home._sanitize_home_fact('a/slash') == 'aslash'