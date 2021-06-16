import numpy as np

from utilites import load, dump
from itertools import product
from copy import deepcopy

data = load('data/normalized_table.json')

sum_by_region = {}
sum_by_industry = {}
sum_by_region_total = {}

years = data.keys()

for year in years:
    sum_by_region.update({year:{}})
    sum_by_industry.update({year:{}})
    regions = data[year]
    for region in regions:
        sum_by_region[year].update({region:0})
        industries = data[year][region]
        for industry in industries:
            sum_by_region[year][region] += data[year][region][industry]

    for industry in industries:
        sum_by_industry[year].update({industry:0})
        for region in regions:
            sum_by_industry[year][industry] += data[year][region][industry]
            

for year in years:
    sum_by_region_total.update({year:0})
    regions = sum_by_region[year]
    for region in regions:
        sum_by_region_total[year] += sum_by_region[year][region]

LQ = {}
for year in years:
    regions = data[year]
    LQ.update({year:{}})
    for region in regions:
        industries = data[year][region]
        LQ[year].update({region:{}})
        for industry in industries:
            B2  = data[year][region][industry]
            _E2 = sum_by_region[year][region]
            B_8 = sum_by_industry[year][industry]
            _E_8 = sum_by_region_total[year]
            try:
                v = (B2/_E2)/(B_8/_E_8)
            except ZeroDivisionError:
                v = 0
            LQ[year][region].update({industry:v})
            
dump(LQ, 'data/LQ.json')

M = {}
for year in LQ:
    regions = LQ[year]
    M.update({year:{}})
    for region in regions:
        industries = LQ[year][region]
        M[year].update({region:{}})
        for industry in industries:
            B12 = LQ[year][region][industry]
            v = 1 if B12 > 1 else 0
            M[year][region].update({industry:v})
            
dump(M, 'data/M.json')

ubiquity = {}

for year in M:
    regions = M[year]
    ubiquity.update({year:{}})
    for region in regions:
        industries = M[year][region]
        for industry in industries:
            try:
                ubiquity[year][industry] += M[year][region][industry]
            except KeyError:
                ubiquity[year].update({industry:M[year][region][industry]})
                
dump(ubiquity, 'data/ubiquity.json')

diversity = {}

for year in M:
    diversity.update({year:{}})
    for region in regions:
        for industry in industries:
            try:
                diversity[year][region] += M[year][region][industry]
            except KeyError:
                diversity[year].update({region:M[year][region][industry]})
                
dump(diversity, 'data/diversity.json')

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
    
    
    