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
        assert rez
    except (KeyError, AssertionError):
        sleep(60)
        x = post(
            'https://html.duckduckgo.com/html/', 
            data={'q':industry_name.replace(' ', '+')}, 
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
        ).content
        dom = BeautifulSoup(x)
        x = dom.text
        open('/tmp/%s.html' % industry_name[0:30], 'w').write(dom.prettify())
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
            industry_list += [' '.join(industry.split())]
            
industry_set = sorted(set(industry_list))


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
    

b_list = list(industries.values())

open('/tmp/out.csv', 'w').write('^'.join([''] + b_list) + '\n')
for i in range(len(rez)):
    open('/tmp/out.csv', 'a').write('^'.join([b_list[i]] + [ str(round(x, 4)).replace('.',',') for x in rez[i] ]) + '\n')
    

rez[rez==1] = 0
n = 0
pairs = []
for industry in industry_set:
    k = np.argmax(rez[n])
    w = rez[n, k]
    if w > 0.75:
        to_pair = industry_set[k]
        pairs += [(industry, to_pair, w)]
    n += 1
