import numpy as np
from itertools import product
from copy import deepcopy
from utilites import load, dump

def set_ones(k_dict):
    rez = deepcopy(k_dict)
    for year in rez:
        for region in rez[year]:
            rez[year][region] = 1
    return rez

def calc_industry_summ(year, region_a, region_b, k_c_0, k_p_0):
    val = 0

    for industry in industries:
        try:
            val += (M[year][region_a][industry] * M[year][region_b][industry]) /\
                         (k_c_0[year][region_a] * k_p_0[year][industry])
        except ZeroDivisionError:
            val += 0
    return val

M = load('data/M.json')
diversity = load('data/diversity.json')
ubiquity = load('data/ubiquity.json')

k_c_0 = diversity
k_p_0 = ubiquity
N = 85
Mcc = np.zeros((len(years),len(regions),len(regions)))

y = 0
for year in years:
    c0 = 0
    for region_a in regions:
        c1 = 0
        for region_b in regions:
            Mcc[y, c0, c1] = calc_industry_summ(year, region_b, region_a, k_c_0, k_p_0)
            c1 += 1
        c0 += 1
    y += 1 
    

# k_c_n = set_ones(k_c_0)
k_c_n = deepcopy(k_c_0)

for n in range(N):
    y = 0
    for year in years:
        c0 = 0
        for region_a in regions:
            v = 0
            c1 = 0
            for region_b in regions:
                v += Mcc[y,c0,c1] * k_c_n[year][region_b]
                c1 += 1
            k_c_n[year][region_a] = v
            c0 += 1
        y += 1
    print(k_c_n['2019']['алтайский край'])
    
    
    