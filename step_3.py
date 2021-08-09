import numpy as np
from itertools import product
from copy import deepcopy
from utilites import load, dump

M = load('data/M.json')
diversity = load('data/diversity.json')
ubiquity = load('data/ubiquity.json')

years = M.keys()
regions = M['2019'].keys()
industries = M['2019']['алтайский край']

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

def calc_Mcc(years, regions, k_c_n, k_p_n):
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
    
    return Mcc

k_c_0 = diversity
k_p_0 = ubiquity
N = 1
Mcc = calc_Mcc(years, regions, k_c_0, k_p_0)

# k_c_n = set_ones(k_c_0)
k_c_n = deepcopy(k_c_0)
k_c_n1 = deepcopy(k_c_0)

for n in range(N):
    print(k_c_n['2019']['республика дагестан'])
    y = 0
    if n % 2 != 0: k_c_n1 = deepcopy(k_c_n)
    for year in years:
        c0 = 0
        for region_a in regions:
            v = 0
            c1 = 0
            for region_b in regions:
                v += Mcc[y,c0,c1] * k_c_n1[year][region_b]
                c1 += 1
            k_c_n[year][region_a] = v
            c0 += 1
        y += 1
    Mcc = calc_Mcc(years, regions, k_c_n, k_p_0)
    
    w, v = np.linalg.eig(Mcc[0])
    K = v[1]
    out = (K - np.average(K) )/ np.std(K)
    x = [ x.round(3) for x in out ]
    test = list(zip(regions, x))
    test = sorted(test, key=lambda x:x[1])
    
    print(test[-1])