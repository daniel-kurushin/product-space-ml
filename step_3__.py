import numpy as np
from itertools import product
from copy import deepcopy
from utilites import load, dump

# Считать рабочей версией

MM = load('data/M.json')

diversity = load('data/diversity.json')
ubiquity = load('data/ubiquity.json')

def set_ones(k_dict):
    rez = deepcopy(k_dict)
    for year in rez:
        for region in rez[year]:
            rez[year][region] = 1
    return rez

def calc_industry_summ(year, region_a, region_b, k_p_0):
    val = 0

    for industry in industries:
        try:
            val += (M[year][region_a][industry] * M[year][region_b][industry]) /\
                                (k_p_0[year][industry])
        except ZeroDivisionError:
            val += 0
    return val

def calc_Mcc(years, regions, k_p):
    Mcc = np.zeros((len(years),len(regions),len(regions)))
    
    y = 0
    for year in years:
        c0 = 0
        for region_a in regions:
            c1 = 0
            for region_b in regions:
                v = calc_industry_summ(year, region_a, region_b, k_p)
                Mcc[y, c0, c1] = v if v != 0 else 0.0001
                c1 += 1
            c0 += 1
        y += 1 
    
    return Mcc

def diag_diversity(diversity):
    rez = np.zeros((len(years), len(regions), len(regions)))
    i = 0
    for year in years:
        j, k = 0, 0
        for region in regions:
            v = diversity[year][region]
            rez[i,j,k] = v if v > 0 else 100000
            j += 1
            k += 1
        i += 1
    return rez


for M in [MM]:
    years = M.keys()
    regions = M['2019'].keys()
    industries = M['2019']['алтайский край']
   
    k_c_0 = diag_diversity(diversity)
    k_p_0 = ubiquity
    N = 1
    Mcc = calc_Mcc(years, regions, k_p_0)
    
    # k_c_n = set_ones(k_c_0)
    k_c_n = deepcopy(k_c_0)
    k_c_n1 = deepcopy(k_c_0)
    
    ECI = np.zeros_like(Mcc)
    
    i = 0
    for year in years:
        ECI[i] = np.linalg.inv(k_c_0[i]).dot(Mcc[i])
        i += 1
    
    
    i = 0
    f = open('/tmp/out.csv', 'w')
    for year in years:
        w, v = np.linalg.eig(ECI[i])
        K = v[1]
        f.write("%s\n" % ", ".join([ '"%s"' % str(x).replace('.',',') for x in K ]))
        out = (K - np.average(K) )/ np.std(K)
        x = [ x.round(3) for x in out ]
        test = list(zip(regions, x))
        test = sorted(test, key=lambda x:x[1])
        m0 = 'город москва столица российской федерации город федерального значения'
        m1 = 'город федерального значения севастополь'
        m2 = 'республика крым'
        print(year, [ x[1] for x in test if x[0] == m0], [ x[1] for x in test if x[0] == m1], [ x[1] for x in test if x[0] == m2])
        i += 1

    f.close()
