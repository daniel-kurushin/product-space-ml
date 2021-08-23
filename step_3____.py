import numpy as np
from itertools import product
from copy import deepcopy
from utilites import load, dump

# Считать рабочей версией

M = load('data/M.json')
ECI = []

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

def calc_region_summ(year, industry_a, industry_b, k_c_0):
    val = 0

    for region in regions:
        try:
            val += (M[year][region][industry_a] * M[year][region][industry_b]) /\
                                (k_c_0[year][region])
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

def calc_Mpp(years, industries, k_p):
    Mpp = np.zeros((len(years),len(industries),len(industries)))
    
    y = 0
    for year in years:
        c0 = 0
        for industry_a in industries:
            c1 = 0
            for industry_b in industries:
                v = calc_region_summ(year, industry_a, industry_b, k_p)
                Mpp[y, c0, c1] = v if v != 0 else 0.0001
                c1 += 1
            c0 += 1
        y += 1 
    
    return Mpp

def diag_diversity(diversity):
    rez = np.zeros((len(years), len(regions), len(regions)))
    i = 0
    for year in years:
        j, k = 0, 0
        for region in regions:
            v = diversity[year][region]
            rez[i,j,k] = v if v > 0 else 0.0001
            j += 1
            k += 1
        i += 1
    return rez

def diag_ubiquity(ubiquity):
    rez = np.zeros((len(years), len(industries), len(industries)))
    i = 0
    for year in years:
        j, k = 0, 0
        for industry in industries:
            v = ubiquity[year][industry]
            rez[i,j,k] = v if v > 0 else 0.0001
            j += 1
            k += 1
        i += 1
    return rez

years = M.keys()
regions = M['2019'].keys()
industries = M['2019']['алтайский край']
   
k_c_0 = diag_diversity(diversity)
k_p_0 = ubiquity
Mcc = calc_Mcc(years, regions, k_p_0)
Mpp = calc_Mpp(years, industries, diversity)
k_c_n = deepcopy(k_c_0)
k_c_n1 = deepcopy(k_c_0)

ECI = np.zeros_like(Mcc)

i = 0
for year in years:
    ECI[i] = np.linalg.inv(k_c_0[i]).dot(Mcc[i])
    i += 1

k_p_0 = diag_ubiquity(ubiquity)
PCI = np.zeros_like(Mpp)

i = 0
for year in years:
    PCI[i] = np.linalg.inv(k_p_0[i]).dot(Mpp[i])
    i += 1

out = []

i = 0
for year in years:
    S = sum(ECI[i])
    j = 0
    outt = []
    for region in regions:
        outt += [(S[j], region)]
        j += 1
    outt = [ x[1] for x in sorted(outt, key=lambda x: x[0]) ]
    out += [outt]

    i += 1

x = np.rot90(np.array(out))
open('/tmp/out_a.csv', 'w')
for i in range(len(x)):
    for j in range(len(x[i])):
        open('/tmp/out_a.csv', 'a').write("^ %s" % x[i,j])
    open('/tmp/out_a.csv', 'a').write("\n")
    
out = []

i = 0
for year in years:
    S = sum(PCI[i])
    j = 0
    outt = []
    for industry in industries:
        outt += [(S[j], industry)]
        j += 1
    outt = [ x[1] for x in sorted(outt, key=lambda x: x[0]) ]
    out += [outt]

    i += 1

x = np.rot90(np.array(out))
open('/tmp/out_b.csv', 'w')
for i in range(len(x)):
    for j in range(len(x[i])):
        open('/tmp/out_b.csv', 'a').write("^ %s" % x[i,j])
    open('/tmp/out_b.csv', 'a').write("\n")