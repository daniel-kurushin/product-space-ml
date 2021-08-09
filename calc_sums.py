import numpy as np

from utilites import load, dump
from copy import deepcopy

data = load('data/normalized_table.json')

x_regions = [ x.lower() for x in ["Алтайский край", "Амурская область", "Архангельская область (кроме Ненецкого автономного округа)", "Астраханская область", "Белгородская область", "Брянская область"] ]
x_industries = [ x.lower() for x in [
"Выращивание однолетних культур",
"Выращивание многолетних культур",
"Животноводство",
"Смешанное сельское хозяйство",
"Деятельность вспомогательная в области производства сельскохозяйственных культур и послеуборочной обработки сельхозпродукции",
"Охота, отлов и отстрел диких животных, включая предоставление услуг в этих областях",
"Лесоводство и прочая лесохозяйственная деятельность",
"Лесозаготовки",
"Предоставление услуг в области лесоводства и лесозаготовок",
"Рыболовство",
"Рыбоводство",
]]

sum_by_region = {}
sum_by_industry = {}
sum_by_region_total = {}

years = data.keys()

def sigma_p(x):
    return 1 if x >= 1 else 0

def sigma(x):
    from math import exp
    return 1 / (1 + exp(-x))

years_to_calc = years
#years_to_calc[-1] = 2010

#for year in years_to_calc:
#    regions = data[str(year)]
#    for region in regions:
#        industries = data[str(year)][region]
#        for industry in industries:
#            _in = [ data[str(x)][region][industry] for x in range(2014-5, 2014+6) ]
#            S = np.average(_in)
#            for y in [ str(x) for x in range(2014-5, 2014+6) ]:
#                data[str(y)][region][industry] = S

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
#            if region == "алтайский край" and industry == "выращивание однолетних культур":
#                print(B2, _E2, B_8, _E_8, v)
            LQ[year][region].update({industry:v})
            
dump(LQ, 'data/LQ.json')

#kLQ = {}
#for region in regions:
#    kLQ.update({region:{}})
#    for industry in industries:
#        x = []
#        y = []
#        for year in years:
#            x += [int(year)]
#            y += [LQ[year][region][industry]]
#        k, b = np.polyfit(x, y, 1)
#        kLQ[region].update({industry:[k, b]})
#        
#dump(kLQ, 'data/kLQ.json')
#
#tLQ = deepcopy(LQ)
#
#for year in years:
#    for region in regions:
#        for industry in industries:
#            k, b = kLQ[region][industry]
#            v = k * int(year) + b
#            tLQ[year][region][industry] = v if v > 0 else 0
#
#dump(tLQ, 'data/tLQ.json')
#
M = {}
for year in LQ:
    regions = LQ[year]
    M.update({year:{}})
    for region in regions:
        industries = LQ[year][region]
        M[year].update({region:{}})
        for industry in industries:
            B12 = LQ[year][region][industry]
            v = sigma_p(B12)
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

