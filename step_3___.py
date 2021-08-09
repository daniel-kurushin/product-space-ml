import numpy as np
from itertools import product
from copy import deepcopy
from utilites import load, dump

MM = load('data/M.json')

def set_ones(k_dict):
    rez = deepcopy(k_dict)
    for year in rez:
        for region in rez[year]:
            rez[year][region] = 1
    return rez

def calc_industry_summ(year, region_a, region_b):
    val = 0

    for industry in industries:
        val += (M[year][region_a][industry] * M[year][region_b][industry]) 
    return val

def calc_Mcc(years, regions):
    Mcc = np.zeros((len(years),len(regions),len(regions)))
    
    y = 0
    for year in years:
        c0 = 0
        for region_a in regions:
            c1 = 0
            for region_b in regions:
                v = calc_industry_summ(year, region_a, region_b)
                Mcc[y, c0, c1] = v
                c1 += 1
            c0 += 1
        c0 = 0
        for region_a in regions:
            c1 = 0
            for region_b in regions:
                v = Mcc[y, c0, c0]
                Mcc[y, c0, c1] /= v
                c1 += 1
            c0 += 1
        y += 1 
    
    return Mcc

for M in [MM]:
    years = M.keys()
    regions = M['2019'].keys()
    industries = M['2019']['алтайский край']
   
    Mcc = calc_Mcc(years, regions)
    
