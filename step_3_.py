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

years = M.keys()
regions = M['2018'].keys()
industries = M['2018']['алтайский край'].keys()

k_c_0 = diversity
k_p_0 = ubiquity
N = 1

k_c_n = deepcopy(k_c_0)
k_c_n1 = deepcopy(k_c_0)
k_p_n = deepcopy(k_p_0)

for n in range(N):
    for year in years:
        for region in regions:
            v = 0
            for industry in industries:
                v += M[year][region][industry] * k_p_n[year][industry]
            try:
                k_c_n1[year][region] = (1 / k_c_0[year][region]) * v
            except ZeroDivisionError:
                k_c_n1[year][region] = 0
                
    for year in years:
        for industry in industries:
            v = 0
            for region in regions:
                v += M[year][region][industry] * k_c_n[year][region]
            try:
                k_p_n[year][industry] = (1 / k_p_0[year][industry]) * v
            except ZeroDivisionError:
                k_p_n[year][industry] = 0
                
    k_c_n = deepcopy(k_c_n1)


Mcc = np.zeros((len(years),len(regions),len(regions)))

y = 0
for year in years:
    c0 = 0
    for region_a in regions:
        c1 = 0
        for region_b in regions:
            Mcc[y, c0, c1] = calc_industry_summ(year, region_a, region_b, k_c_n, k_p_n)
            c1 += 1
        c0 += 1
    y += 1 
    
i = 0
for year in years:
    w, v = np.linalg.eig(Mcc[i])
    K = v[1]
    out = (K - np.average(K) )/ np.std(K)
    x = [ x.round(3) for x in out ]
    test = list(zip(regions, x))
    test = sorted(test, key=lambda x:x[1])
    m0 = 'город москва столица российской федерации город федерального значения'
    m1 = 'город федерального значения севастополь'
    m2 = 'республика крым'
    print(year, [ x[1] for x in test if x[0] == m0], [ x[1] for x in test if x[0] == m1], [ x[1] for x in test if x[0] == m2])
    i += 1