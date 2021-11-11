import numpy as np

from utilites import load, dump
from xlrd import open_workbook
from math import log
from data.grp2019 import grp

complexity = load('data/complexity.json')
regions = list(complexity.keys())

region_to_region = load('data/region-to-region.json')

def calc_theil_index(neighbours): 
    R = len(neighbours)
    Y = sum([ grp[r] for r in neighbours ])
    T_m = 0
    for region in neighbours:
        Y_r = grp[region]
        v = (Y_r / Y) * log(Y_r/(Y/R))
        print(region, v)
        T_m += v
    return T_m, Y

def get_reg_name(x):
    try:
        regname = region_to_region[x]
    except KeyError:
        assert x in regions
        regname = x
    return regname

def get_region_border_map():
    neib85 = open_workbook('data/neib85.xls').sheet_by_index(0)
    M = {}
    
    for row in range(1, neib85.nrows):
        for col in range(1, neib85.ncols):
            a, b = [ region_to_region[x.lower()] for x in [neib85.cell(col, 0).value, neib85.cell(0, row).value]]
            
            if neib85.cell(col, row).value:
                try:
                    M[a] += [b]
                except KeyError:
                    M.update({a:[b]})
    return M
       

def get_region_properties():
    cluster_data = open_workbook('data/cluster_in_data.xlsx').sheet_by_index(0)
    N = {}
    
    for row in range(1, cluster_data.nrows):
        regname = get_reg_name(cluster_data.cell(row, 0).value.lower().strip())
        
        seaports                   = int(cluster_data.cell(row,  1).value) * 0.04
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

def get_region_clusters(border_map, region_properties, sorted_regions):
    def get_properties(region):
        return np.array([ region_properties[region][x][0] for x in region_properties[region] ])
    
    def get_neighbours_complexity(current_neighbours):
        rez = 1
        for neighbour in current_neighbours:
            rez *= complexity[neighbour]
        return np.sqrt(rez)
    
    def find_more_neighbours(current_neighbours, border_map, regions):
        
        rez = set()
        a = sum(calc_neighbours_weight(current_neighbours))
        c = get_neighbours_complexity(current_neighbours)
        
        for neighbour in current_neighbours:
            for region in border_map[neighbour]:
                if region in regions:
                    b = sum(calc_neighbours_weight(current_neighbours | {region}))
                    d = get_neighbours_complexity(current_neighbours | {region})
                    if b > a and d > c:
                        open('/tmp/x_%s.dat' % sample,'a').write("%s\n" % b)
                        a = b
                        c = d
                        rez |= {region}
        return rez
        
    def calc_neighbours_weight(_neighbours):
        neighbours = _neighbours.copy()
        region = neighbours.pop()
        rez = get_properties(region) 
        while neighbours:
            region = neighbours.pop()    
            rez += get_properties(region) 
        return rez
    
    regions = [ x[0] for x in sorted_regions ]
    rez = {}
    
    while regions:
        sample = regions.pop()
        print("Processing ", sample)
        neighbours = {sample}
        weight = sum(calc_neighbours_weight(neighbours) > 0)
        
        n = 0
        while weight < 12 and n < 15:
            neighbours |= find_more_neighbours(neighbours, border_map, regions)
            weight = sum(calc_neighbours_weight(neighbours) > 0)
            n += 1

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
                'сумма ВРП по кластеру': Y_m,
            }
        })
        print("done")
        
    return rez
        
def calc_T_within(region_clusters):
    Y = sum([ grp[x] for x in grp ])
    v = 0
    for cluster in region_clusters:
        T_m = region_clusters[cluster]["индекс Тейла"]
        Y_m = region_clusters[cluster]["сумма ВРП по кластеру"]
        v += (T_m * Y_m) / Y
    return v
    
def calc_T_between(region_clusters):
    Y = sum([ grp[x] for x in grp ])
    R = len(grp.keys())    
    v = 0
    for cluster in region_clusters:
        R_m = len(region_clusters[cluster]['состав кластера'])
        T_m = region_clusters[cluster]["индекс Тейла"]
        Y_m = region_clusters[cluster]["сумма ВРП по кластеру"]
        v += Y_m / Y * log((Y_m / R_m) / (Y / R))
    return v
    
def filter_bad_clusters(region_clusters):
    pass

border_map = get_region_border_map()
region_properties = get_region_properties()
sorted_regions = sort_regions_by_properties(region_properties)

region_clusters = get_region_clusters(border_map, region_properties, sorted_regions)
T_within = calc_T_within(region_clusters)
T_between = calc_T_between(region_clusters)

filtered_region_clusters = filter_bad_clusters(region_clusters)

dump(region_clusters, 'data/clusters_out.json')

