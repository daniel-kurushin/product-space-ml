from utilites import load, dump
from itertools import product

data = load('data/BD2009-2019.json')

industry_mapping = load('data/mapping_table_a.json')  
region_mapping = load('data/mapping_table_region.json')

regions = open('data/etalon_regions.csv').readline().lower().split('^')
industries = [ " ".join(x.lower().split()) for x in data["2019"]["амурская область"].keys() ]

def get_value(data, year, region, industry):
    reg = [region, region_mapping[region] ]
    ind = [ industry, industry_mapping[industry] ]
    v = None
    for r, i in product(reg, ind):
        try:
            v = data[year][r][i]
        except KeyError:
            pass
    assert v is not None
    return v

rez = {}

for year in data:
    rez.update({year:{}})
    for r, i in product(regions, industries):
        v = get_value(data, year, r, i)
        try:
            rez[year][r].update({i:v})
        except KeyError:
            rez[year].update({r:{}})
            rez[year][r].update({i:v})
            
dump(rez, 'data/normalized_table.json')