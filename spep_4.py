import numpy as np
from utilites import load, dump, wrap, wpt
from dict_to_xls import dict_to_xls

M = load('data/M.json')
k_p_0 = load('data/ubiquity.json')

years = M.keys()
regions = M['2019'].keys()
industries = M['2019']['алтайский край']

Fpp = {}

for year in years:
    Fpp.update({year:{}})
    for industry_a in industries:
        Fpp[year].update({industry_a:{}})
        for industry_b in industries:
            Fpp[year][industry_a].update({industry_b:0})
            s = 0
            for region in regions:
                s += M[year][region][industry_a] * M[year][region][industry_b]
            
            Fpp[year][industry_a][industry_b] = s / max(k_p_0[year][industry_a], k_p_0[year][industry_b])
        
years = ['2009', '2019']

for year in years:
    graph = "digraph g {\n"
    pairs = []
    
    for industry_a in industries:
        for industry_b in industries:
            if industry_a != industry_b and \
               Fpp[year][industry_a][industry_b] > 0.5 and \
               (industry_a,industry_b) not in pairs:
                 a = wrap(wpt, industry_a)
                 b = wrap(wpt, industry_b)
                 c = int(18 * Fpp[year][industry_a][industry_b] - 8)
                 graph += '\t"%s" -> "%s" [penwidth=%s]\n' % (a, b, c)
                 pairs += [(industry_b,industry_a)]
    
    graph += "}\n"
        
    open('/tmp/graph.%s.dot' % year, 'w').write(graph)
    
dict_to_xls('/tmp/Fpp.xlsx', Fpp, {'sheets':0,'columns':1, 'rows':2})
