import re

from requests import post
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
    region_terms = load('region_terms.json')
except FileNotFoundError:
    region_terms = {}

def get_region_description(region_name):
    def is_russian(term):
        try:
            rez = re.match(r'[а-яё ]+', term).group() == term
        except AttributeError as e:
            rez = 0
        return rez
    
    try:
        rez = region_terms[region_name]
    except KeyError:
        sleep(.5)
        x = post(
            'https://html.duckduckgo.com/html/', 
            data={'q':region_name.replace(' ', '+')}, 
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
        ).content
        x = BeautifulSoup(x).text
        rez = [
            t for t in te(x, strings=1) if t.count(' ') > 0 and t not in stopterms and is_russian(t)
        ]
        region_terms.update({region_name:rez})
        dump(region_terms, 'region_terms.json')
    return tuple(rez)


for year in data.keys():
    for region in data[year].keys():
        region_list += [region]
        for industry in data[year][region].keys():
            industry_list += [industry]
            
region_set = set(region_list)


regions = {}
for region in region_set:
    regions.update({get_region_description(region):region})
    
rez = np.zeros((len(regions), len(regions)))
idx = list(product(range(len(regions)), range(len(regions))))
n = 0

a_list = regions.keys()

for a, b in product(a_list, a_list):
    v = ( compare_terms(a, b) + compare_terms(a, b) ) / 2
    i, j = idx[n]
    rez[i,j] = v
    n += 1
    
for i in range(len(regions)):
    _min = min(rez[i])
    _max = max(rez[i] - _min)
    rez[i] = (rez[i] - _min) / _max if _max else 0
    
