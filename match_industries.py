import re

from requests import get, post
from bs4 import BeautifulSoup
from rutermextract import TermExtractor
from utilites import load, dump
import numpy as np
from itertools import product
from utilites import compare_phrase as compare_terms
from time import sleep

stopterms = {'республика', 'город', 'край'}

data = load('data/BD2009-2019.json')

region_list = []
industry_list = []
te = TermExtractor()

try:    
    industry_terms = load('industry_terms.json')
except FileNotFoundError:
    industry_terms = {}

def get_industry_description(industry_name):
    def is_russian(term):
        try:
            rez = re.match(r'[а-яё ]+', term).group() == term
        except AttributeError as e:
            rez = 0
        return rez
    
    try:
        rez = industry_terms[industry_name]
    except KeyError:
        sleep(.5)
        x = post(
            'https://html.duckduckgo.com/html/', 
            data={'q':industry_name}, 
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
        ).content
        x = BeautifulSoup(x).text
        rez = [
            t for t in te(x, strings=1) if t.count(' ') > 0 and t not in stopterms and is_russian(t)
        ]
        industry_terms.update({industry_name:rez})
        dump(industry_terms, 'industry_terms.json')
    return tuple(rez)

for year in data.keys():
    for region in data[year].keys():
        region_list += [region]
        for industry in data[year][region].keys():
            industry_list += [industry]
            
industry_set = set(industry_list)


industries = {}
for industry in industry_set:
    industries.update({get_industry_description(industry):industry})
    
rez = np.zeros((len(industries), len(industries)))
idx = list(product(range(len(industries)), range(len(industries))))
n = 0

a_list = industries.keys()

for a, b in product(a_list, a_list):
    v = ( compare_terms(a, b) + compare_terms(a, b) ) / 2
    i, j = idx[n]
    rez[i,j] = v
    n += 1
    
for i in range(len(industries)):
    _min = min(rez[i])
    _max = max(rez[i] - _min)
    rez[i] = (rez[i] - _min) / _max if _max else 0
    
