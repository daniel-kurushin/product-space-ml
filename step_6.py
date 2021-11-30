import numpy as np

from utilites import load, dump
from xlrd import open_workbook
from math import log
from data.grp2019_ import grp, population

complexity = load('data/complexity.json')
regions = list(complexity.keys())

region_to_region = load('data/region-to-region.json')

def load_region_distance():
    dist = open_workbook('data/region_distance.xls').sheet_by_index(0)
    
    rez = {}
    for row in range(1, dist.nrows):
        for col in range(1, dist.ncols):
            v = dist.cell(col, row).value
            a = region_to_region[dist.cell(col, 0).value.lower()]
            b = region_to_region[dist.cell(0, row).value.lower()]
            
            rez.update({(a,b):v, (b,a):v})
    return rez

def calc_theil_index(neighbours): 
    R = len(neighbours)
    Y = sum([ grp[r] for r in neighbours ]) / sum([ population[r] for r in neighbours ])
    T_m = 0
    for region in neighbours:
        Y_r = grp[region] / population[region]
        v = (Y_r / Y) * log(Y_r/(Y/R))
        T_m += v
    return T_m, Y

def get_reg_name(x):
    try:
        regname = region_to_region[x]
    except KeyError:
        assert x in regions
        regname = x
    return regname

def get_region_distance(a, b):
    a_0 = region_to_region(a)
    b_0 = region_to_region(b)
    b_i = region_distance_index.index(b_0)
    v = region_distance[a_0][b_i]
    return v

def get_region_border_map():
    neib85 = open_workbook('data/neib85.a.xls').sheet_by_index(0)
    M = {}
    
    for row in range(1, neib85.nrows):
        for col in range(1, neib85.ncols):
            a, b = [ region_to_region[x.lower()] for x in [neib85.cell(col, 0).value, neib85.cell(0, row).value]]
            
            v = neib85.cell(col, row).value
            if v:
                try:
                    M[a] += [(b, v)]
                except KeyError:
                    M.update({a:[(b, v)]})
    return M
       

def get_region_properties():
    cluster_data = open_workbook('data/cluster_in_data.xlsx').sheet_by_index(0)
    N = {}
    
    for row in range(1, cluster_data.nrows):
        regname = get_reg_name(cluster_data.cell(row, 0).value.lower().strip())
        
        seaports                   = int(cluster_data.cell(row, 1).value) * 0.00
        airports                   = int(cluster_data.cell(row, 2).value) * 0.10
        we_transport_corridor      = int(cluster_data.cell(row, 3).value) * 0.08
        ns_transport_corridor      = int(cluster_data.cell(row, 4).value) * 0.08
        
        ind_parks                  = int(cluster_data.cell(row, 5).value) * 0.05
        cluster_in_region          = int(cluster_data.cell(row, 6).value) * 0.05
        sp_econ_zone               = int(cluster_data.cell(row,7).value) * 0.10
        
        education_priority_2030    = int(cluster_data.cell(row, 8).value) * 0.10
        
        onco_institutions          = int(cluster_data.cell(row, 9).value) * 0.05
        cardio_centers             = int(cluster_data.cell(row,10).value) * 0.05
        medical_research_centers_  = int(cluster_data.cell(row, 11).value) * 0.10
        
        centers_of_economic_growth = int(cluster_data.cell(row, 12).value) * 0.20    
          
        N.update({
            regname:
                {
                    'Наличие морских портов' : (seaports, "Транспорт"),
                    'Наличие международных аэропортов' : (airports, "Транспорт"),
                    'Есть выход к транспортному коридору "Запад-Восток"' : (we_transport_corridor, "Транспорт"),
                    'Есть выход к транспортному коридору "Север-Юг"' : (ns_transport_corridor, "Транспорт"),
                    'Индустриальные парки' : (ind_parks, "Пространственное развитие"),
                    'Кластер' : (cluster_in_region, "Пространственное развитие"),
                    'Особые экономические зоны' : (sp_econ_zone, "Пространственное развитие"),
                    'Образование Приоритет 2030' : (education_priority_2030, "Образование"),
                    'Онкологические учреждения России ' : (onco_institutions, "Здравоохранение"),
                    'Кардиологические центры' : (cardio_centers, "Здравоохранение"),
                    'Сеть национальных медицинских исследовательских центров ' : (medical_research_centers_, "Здравоохранение"),
                    'Текущие центры экономического роста' : (centers_of_economic_growth,"Экономика"),
                }
            }
        )
    dump(N, 'data/region_properties.json')
    return N

def sort_regions_by_properties(N):
    out = []
    for region in N:
        regname = region
        value = np.sum(np.array([ N[region][c][0] for c in N[region] ]))
        out += [(regname, value)]
        
    out = sorted(out, key=lambda x : x[1])
    
    dump(out, 'data/sorted_regions.json')
    return out

def calc_neighbours_weight(_neighbours):
    def get_properties(region):
        return np.array([ region_properties[region][x][0] for x in region_properties[region] ])

    neighbours = _neighbours.copy()
    region = neighbours.pop()
    rez = get_properties(region) 
    while neighbours:
        region = neighbours.pop()    
        rez += get_properties(region) 
    return rez

def get_region_clusters(border_map, region_properties, sorted_regions):
    
    def get_neighbours_complexity(current_neighbours):
        rez = 1
        for neighbour in current_neighbours:
            rez *= complexity[neighbour]
        return np.sqrt(rez)
    
    def find_more_neighbours(core, current_neighbours, border_map, regions):
        
        rez = set()
        a = sum(calc_neighbours_weight(current_neighbours))
        c = get_neighbours_complexity(current_neighbours)
        
        for neighbour in sorted(current_neighbours):
            for region in [ x[0] for x in sorted(border_map[neighbour], key=lambda x:region_distance[(x[0], core)], reverse=0) ]:
                if region in regions:
                    b = sum(calc_neighbours_weight(current_neighbours | {region}))
                    d = get_neighbours_complexity(current_neighbours | {region})
                    if b > a and d > c:
                        a = b
                        c = d
                        rez |= {region}
        return rez
        
    regions = [ x[0] for x in sorted_regions ]
    rez = {}
    
    while regions:
        sample = regions.pop()
        print("Processing ", sample)
        neighbours = {sample}
        weight = sum(calc_neighbours_weight(neighbours) > 0)
        
        n = 0
        while ( weight < 11 and n < 20 ) or n < 3:
            neighbours |= find_more_neighbours(sample, neighbours, border_map, regions)
            weight = sum(calc_neighbours_weight(neighbours) > 0)
            n += 1
            T_m, Y_m = calc_theil_index(neighbours)
            open('/tmp/log', 'a').write("%s %s\n" % (T_m, Y_m/10000000))

        for neighbour in neighbours:
            try:
                print("    Popping region ", neighbour, "...", end='')
                regions.pop(regions.index(neighbour))
                print("done")
            except ValueError:
                print("FAIL!")

        T_m, Y_m = calc_theil_index(neighbours)
        rez.update({sample:{
                'состав кластера':sorted(list(neighbours)),
                'вес кластера': int(weight),
                'индекс Тейла': T_m,
                'подушевой ВРП по кластеру': Y_m,
            }
        })
        print("done")
        
    return rez
        
def calc_T_within(region_clusters):
    Y = sum([ grp[x] for x in grp ]) / sum([ population[r] for r in population ])
    v = 0
    for cluster in region_clusters:
        T_m = region_clusters[cluster]["индекс Тейла"]
        Y_m = region_clusters[cluster]["подушевой ВРП по кластеру"]
        v += (T_m * Y_m) / Y
    return v
    
def calc_T_between(region_clusters):
    Y = sum([ grp[x] for x in grp ]) / sum([ population[r] for r in population ])
    R = len(grp.keys())    
    v = 0
    for cluster in region_clusters:
        R_m = len(region_clusters[cluster]['состав кластера'])
        T_m = region_clusters[cluster]["индекс Тейла"]
        Y_m = region_clusters[cluster]["подушевой ВРП по кластеру"]
        v += Y_m / Y * log((Y_m / R_m) / (Y / R))
    return v
    
def filter_bad_clusters(region_clusters):
    from itertools import product
    from pprint import pprint
    from copy import deepcopy
    
    region_clusters = deepcopy(region_clusters)
    
    bad_clusters, good_clusters = [], []
    for cluster in region_clusters.keys():
        if len(region_clusters[cluster]["состав кластера"]) < 2:
            bad_clusters += [cluster]
        else:
            good_clusters += [cluster]

    variants = {}
    for good, bad in product(good_clusters, bad_clusters):
        try_region_clusters = deepcopy(region_clusters[good])
        x = calc_theil_index(try_region_clusters["состав кластера"])[0]
        try_region_clusters["состав кластера"] += region_clusters[bad]["состав кластера"]
        y = calc_theil_index(try_region_clusters["состав кластера"])[0]
        delta_T = x - y
        variants.update({(bad, good):delta_T})

    filtered_variants = []
    for (bad, good), v in variants.items():
        bad_neighbours = { r[0] for r in border_map[bad] }
        good_neighbours = set(region_clusters[good]["состав кластера"])
        if bad_neighbours & good_neighbours:
            filtered_variants += [(bad, good, v)]

    filtered_variants = sorted(filtered_variants, key=lambda x:x[2])
    
    added = []
    for bad, good, v in filtered_variants:
        try:
            assert bad not in added
            region_clusters[good]['состав кластера'] += [bad]
            a, b = calc_theil_index(region_clusters[good]['состав кластера'])
            region_clusters[good]['индекс Тейла'] = a
            region_clusters[good]['подушевой ВРП по кластеру'] = b
            region_clusters[good]["вес кластера"] = int(sum(calc_neighbours_weight(region_clusters[good]['состав кластера']) > 0))
            del region_clusters[bad]
            added += [bad]
        except AssertionError:
            print(bad, 'уже добавлен')
        except KeyError as s:
            print(s)
    return region_clusters

border_map = get_region_border_map()
region_distance = load_region_distance()
region_properties = get_region_properties()
sorted_regions = sort_regions_by_properties(region_properties)

region_clusters = get_region_clusters(border_map, region_properties, sorted_regions)

region_clusters = filter_bad_clusters(region_clusters)

T_within = calc_T_within(region_clusters)
T_between = calc_T_between(region_clusters)

region_clusters.update(
    {
         "T_within": T_within, 
         "T_between": T_between, 
    }
)
dump(region_clusters, 'data/clusters_out.json')
