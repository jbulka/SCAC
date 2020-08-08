#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 27 18:22:22 2020

@author: Jordan
"""

import requests
import re
from bs4 import BeautifulSoup as bs
from collections import deque
import math
import os

def find_num_records(soup):
    '''
    This function takes the SCAC filings page and returns the total number
    of records in the database.
    '''
    records = soup.find('div', id = 'records')
    num_records_string = records.find('div', class_ = 'span6').contents[1].text
    num_records = int(re.findall('\d+', num_records_string)[0])
    return num_records

def get_soup(url):
    '''This function returns the soup from a given url.'''
    return bs(requests.get(url).content, 'html.parser')

def append_urls(soup, d):
    '''
    This function appends the filings from a SCAC page to a deque, d.
    '''
    filings = soup.find_all('tr', class_ = 'table-link')
    for filing in filings:
        id_str = re.findall('\?id=\d+', str(filing))[0]
        filing_url = r'http://securities.stanford.edu/filings-case.html' + id_str
        d.append(filing_url)
        
# construct the url and get soup of first page
page_url = r'http://securities.stanford.edu/filings.html?page=1'
soup = get_soup(page_url)

# find the number of records in the database and use it to compute the number
# of url pages
num_records = find_num_records(soup)
num_pages = math.ceil(num_records/20)

# initialize a deque and append the records from the first page to the deque
d = deque()
append_urls(soup, d)
print('Processed page 1.')

# iterate over the remaining pages and append the filing urls to the deque
for i in range(2, num_pages + 1):
    page_url = r'http://securities.stanford.edu/filings.html?page=' + str(i)
    soup = get_soup(page_url)
    append_urls(soup, d)
    print('Processed page {}.'.format(i))
    
# open a csv file to store the data
os.chdir(r'/Users/Jordan/Documents/Projects/SCAC/Data/')
with open('scac_filings.tsv', 'w') as f:
    
    # write the column names
    f.write('''case_id\t
    defendant_cmpy_nm\t
    sector\t
    industry\t
    hq\t
    ticker\t
    mkt\t
    mkt_status\t
    filing_dt\t
    case_status\t
    case_status_dt\t
    court\t
    judge\t
    class_prd_start\t
    class_prd_end\t
    complaint_txt\n''')
    
    # pop filing urls from the deque, process them, and write the data to f
    while d:
        soup = get_soup(d.pop())
        '*** PROCESS DATA HERE ***'
        '*** WRITE DATA HERE ***'
    

    


