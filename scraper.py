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

def write_data(f, data):
    '''
    This function writes the values from the dictionary 'data' to the .tsv file 'f'.
    '''
    
def main():
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
        f.write('''case_id\tdefendant_cmpy_nm\tsector\tindustry\thq\tticker\tmkt\tmkt_status\tfiling_dt\tcase_status\tcourt\tjudge\tclass_prd_start\tclass_prd_end\tcomplaint_txt\n''')
        
        # initialize counter for case_id
        case_id = 1
        
        # pop filing urls from the deque, process them, and write the data to f
        while d:
            
            # initialize data dictionary and get soup
            data = {'case_id': str(case_id)}
            soup = get_soup(d.pop())
            
            print('Parsing Case {} data...'.format(case_id))
            
            # extract large sections
            summary = soup.find_all('section', {'id': 'summary'})[0]
            company = soup.find_all('section', {'id': 'company'})[0]
            fic = soup.find_all('section', {'id': 'fic'})[0]
            
            # case status and case status dt
            case_status_txt = re.sub(r"\t", ' ', re.sub(r"\n|\xa0", '', summary.find_next('p').text))
            data['case_status'] = re.findall(r'Case Status:\s+[a-zA-Z]+', case_status_txt)[0].split(' ')[-1]
            data['case_status_dt'] = re.findall(r'\d{2}/\d{2}/\d{4}', case_status_txt)[0]
            
            # complaint text
            complaint_txt = summary.find_all('div', {'class': 'span12', 'style':'background-color: #ffffff;'})[0].text
            data['complaint_txt'] = re.sub(r"\t|\n|\\", "", complaint_txt).strip()
            
            # company and securities info
            cmpy_nm = company.find('div', {'class': 'page-header'}).h4.text
            data['defendant_cmpy_nm'] = re.sub('defendant: ', '', re.sub(r'\t|\n', '', cmpy_nm).lower().strip())
            cmpy_sec = company.find_all('div', {'class': 'row-fluid'})
            dct = {}
            for i in cmpy_sec:
                for j in i.find_all('div', {'class': 'span4'}):
                    key_value = j.text.lower().split(':')
                    dct[key_value[0].strip()] = key_value[1].strip()
            data['mkt'] = dct['company market']
            data['hq'] = dct['headquarters']
            data['industry'] = dct['industry']
            data['mkt_status'] = dct['market status']
            data['sector'] = dct['sector']
            data['ticker'] = dct['ticker symbol']
            
            # court, judge, & class period data
            fic_rows = fic.find_all('div', {'class': 'row-fluid'})
            dct = {}
            for i in fic_rows:
                for j in i.find_all('div', {'class': 'span4'}):
                    key_value = j.text.lower().split(':')
                    dct[key_value[0].strip()] = key_value[1].strip()
            data['class_prd_end'] = dct['class period end']
            data['class_prd_start'] = dct['class period start']
            data['court'] = dct['court']
            data['filing_dt'] = dct['date filed'] 
            data['judge'] = dct['judge']
            
            print('Parsed.')
            
            # write the data to f
            columns = ['case_id', 'defendant_cmpy_nm', 'sector', 'industry', 'hq',
                       'ticker', 'mkt', 'mkt_status', 'filing_dt', 'case_status',
                       'court', 'judge', 'class_prd_start', 'class_prd_end', 'complaint_txt']
            data_str = ''
            for i in range(len(columns)-1):
                data_str = data_str + data[columns[i]] + '\t'
            data_str = data_str + data[columns[len(columns) - 1]] + '\n'
            f.write(data_str)
            
            print('Successfully written data to output file.')
            
            # increment the case_id        
            case_id = case_id + 1
    
        
if __name__ == '__main__':
    main()
