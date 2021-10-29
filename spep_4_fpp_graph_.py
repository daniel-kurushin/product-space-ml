from utilites import load
from voc import voc

M = load('data/M_.json')
k_p_0 = load('data/ubiquity.json')

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
            
            Fpp[year][industry_a][industry_b] = s / max(k_p_0[year][industry_a], k_p_0[year][industry_b])
        

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

for year in years:
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

    for region in regions:
        graph = "digraph g {\n\trankdir=LR\n"
        for node in nodes:
            a_regions = set(get_regions_by_year_industry(year, node))
            shape = 'circle' if region in a_regions else 'plain'
            graph += '\t"%s" [label="%s" shape=%s]\n' % (node, voc[node], shape)
    
        for edge in subgraph:
            a = edge[1]
            b = edge[2]
            c = int(12 * Fpp[year][edge[1]][edge[2]] + 1)
            graph += '\t"%s" -> "%s" [dir=none, penwidth=%s, color=grey]\n' % (a, b, 1)
        graph += "}\n"
            
        open('/tmp/graph.g.%s.%s.dot' % (year, region.replace(' ','_')), 'w').write(graph)
"""
    for industry_a in industries:
        for industry_b in industries:
            if industry_a != industry_b and \
               Fpp[year][industry_a][industry_b] > 0.005 and \
               (industry_a,industry_b) not in pairs:
                 a = wrap(wpt, industry_a)
                 b = wrap(wpt, industry_b)
                 c = 1 # int(13 * Fpp[year][industry_a][industry_b] - 0.3)
                 graph += '\t"%s" -> "%s" [penwidth=%s]\n' % (a, b, c)
                 pairs += [(industry_b,industry_a)]
    
"""