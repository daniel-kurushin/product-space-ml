from utilites import load, dump
from voc import voc

from itertools import product

# Считать рабочей версией

LQP = [1, .7, 0.8, 1.5, 2]
SSP = [.8, .99, .9, .2]

for lqp, ssp in product(LQP, SSP):
    print('lqp =', lqp, 'ssp =', ssp)

    M = load('/tmp/data/M__%s_%s.json' % (lqp, ssp))
    k_p_0 = load('/tmp/data/ubiquity_%s_%s.json' % (lqp, ssp))
    
    years = M.keys()
    regions = M['2019'].keys()
    industries = M['2019']['алтайский край']
    
    
    
    M_rot90 = {}
    
    for year in years:
        M_rot90.update({year:{}})
        for industry in industries:
            M_rot90[year].update({industry:{}})
            for region in regions:
                m = M[year][region][industry]
                M_rot90[year][industry].update({region:m})
                
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
                
                try:
                    Fpp[year][industry_a][industry_b] = s / max(k_p_0[year][industry_a], k_p_0[year][industry_b])
                except ZeroDivisionError:
                    Fpp[year][industry_a][industry_b] = 0
            
    dump(Fpp, '/tmp/data/Fpp_%s_%s.json' % (lqp, ssp))
    
    for year in years:
        for industry in industries:
            Fpp[year][industry][industry] = 0
    
    for year in years:
        for industry_a in industries:
            values = []
            for industry_b in industries:
                values += [Fpp[year][industry_a][industry_b]]
                
            min_value = sorted(values, reverse=1)[:1][-1]
            for industry_b in industries:
                if Fpp[year][industry_a][industry_b] < min_value:
                    Fpp[year][industry_a][industry_b] = 0
                    
                    
    def get_regions_by_year_industry(year, industry):
        rez = []
        for region in regions:
            if M_rot90[year][industry][region]:
                rez += [region]
                
        return rez
    
    year = '2019'
    nodes = set(Fpp[year].keys())
    edges = []
    for industry_a in industries:
        for industry_b in industries:
            w = Fpp[year][industry_a][industry_b]
            a, b = sorted([industry_a, industry_b])
            if (w, a, b) not in edges:
                edges += [(w, a, b)]

    edges = sorted(edges)

    subgraph = [edges[-1]]
    subnodes = set(edges[-1][1:])
    while nodes - subnodes:
        for a, b in [ (x[1], x[2]) for x in edges if (x[1] in subnodes and x[2] not in subnodes) or (x[2] in subnodes and x[1] not in subnodes)][-5:]:
            edge_to_add = sorted([ x for x in edges if (x[1:] == (a, b)) or (x[1:] == (b, a)) ])[-1]
            subnodes |= set((a,b))
            subgraph += [edge_to_add]

    graph = "digraph g {\n\trankdir=LR\n"
    for node in nodes:
        graph += '\t"%s" [label="%s" shape=%s]\n' % (node, voc[node], shape)

    for edge in subgraph:
        a = edge[1]
        b = edge[2]
        c = int(12 * Fpp[year][edge[1]][edge[2]] + 1)
        graph += '\t"%s" -> "%s" [dir=none, penwidth=%s, color=grey]\n' % (a, b, 1)
    graph += "}\n"
        
    open('/tmp/data/graph.g.%s.%s.dot' % (lqp, ssp), 'w').write(graph)
