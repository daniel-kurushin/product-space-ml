from requests import get
from bs4 import BeautifulSoup
from rutermextract import TermExtractor
from utilites import load
import numpy as np
from itertools import product
from utilites import compare_phrase as compare_terms

stopterms = {'республика', 'город', 'край'}

data = load('data/BD2009-2019.json')

region_list = []
industry_list = []
te = TermExtractor()

for year in data.keys():
    for region in data[year].keys():
        region_list += [region]
        for industry in data[year][region].keys():
            industry_list += [industry]
            
industry_set = set(industry_list)
region_set = set(region_list)

regions = {}
for region in region_set:
    regterms = tuple(set(te(region, strings=1)) - stopterms)
    regions.update({regterms:region})
    
rez = np.zeros((len(regions), len(regions)))

i = 0
for region_a in regions:
    j = 0

    for region_b in regions:
        n, weight = 0, 0
        for a, b in product(region_a, region_b):
            print(a, b, compare_terms(a, b))
            v = ( compare_terms(a, b) + compare_terms(a, b) ) / 2
            if v > 0.01:
                weight += v
                n += 1
        rez[i,j] = weight / n if n > 0 else 0
        j += 1
        
    i += 1

for i in range(len(regions)):
    _min = min(rez[i])
    _max = max(rez[i] - _min)
    rez[i] = (rez[i] - _min) / _max if _max else 0
    
region_names = list(regions)

for i in range(len(regions)):
    n = np.argmax(rez[i])    
    print(region_names[i], region_names[n], rez[i][n])